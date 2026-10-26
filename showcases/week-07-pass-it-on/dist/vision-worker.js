import { AutoProcessor, CLIPVisionModelWithProjection, RawImage, env } from './vendor/transformers.min.js';

const root = new URL('./', import.meta.url);
let ready, metadata, textVectors;
const progress = message => postMessage({ type: 'progress', message });

async function read(path, binary = false) {
  const response = await fetch(new URL(path, root));
  if (!response.ok) throw new Error(`Could not open the drawing model asset (${response.status}).`);
  return binary ? response.arrayBuffer() : response.json();
}

async function initialize() {
  if (!ready) ready = (async () => {
    progress('Opening the local drawing model. The first load reads about 89 MB; your drawing stays in this browser.');
    [metadata, textVectors] = await Promise.all([read('data/vision.json'), read('data/vision-text-vectors.bin', true)]);
    textVectors = new Float32Array(textVectors);
    if (textVectors.length !== metadata.candidates.length * 512) throw new Error('Drawing-model candidate data is incomplete.');
    env.allowRemoteModels = false; env.allowLocalModels = true;
    env.localModelPath = new URL('models/', root).href;
    env.useBrowserCache = false; env.useFSCache = false; env.useCustomCache = true;
    env.backends.onnx.wasm.wasmPaths = new URL('vendor/', root).href;
    env.backends.onnx.wasm.numThreads = 1; env.backends.onnx.wasm.proxy = false;
    env.customCache = {
      async match(request) {
        const key = String(request.url || request);
        if (!key.endsWith('/vision_model_quantized.onnx')) return undefined;
        const chunks = [];
        for (let i = 0; i < metadata.parts.length; i++) {
          progress(`Opening drawing model · part ${i + 1} of ${metadata.parts.length}`);
          const part = metadata.parts[i];
          const bytes = await read(`models/clip-vit-base-patch32/${part.file}`, true);
          if (bytes.byteLength !== part.bytes) throw new Error('A drawing-model file is incomplete. Please retry.');
          const digest = await crypto.subtle.digest('SHA-256', bytes);
          const hex = [...new Uint8Array(digest)].map(value => value.toString(16).padStart(2, '0')).join('');
          if (hex !== part.sha256) throw new Error('A drawing-model file failed its integrity check.');
          chunks.push(bytes);
        }
        return new Response(new Blob(chunks), { headers: { 'Content-Type': 'application/octet-stream', 'Content-Length': String(metadata.visionBytes) } });
      },
      async put() {},
    };
    const [processor, model, config] = await Promise.all([
      AutoProcessor.from_pretrained('clip-vit-base-patch32', { local_files_only: true }),
      CLIPVisionModelWithProjection.from_pretrained('clip-vit-base-patch32', { quantized: true, local_files_only: true }),
      read('models/clip-vit-base-patch32/preprocessor_config.json'),
    ]);
    progress('Drawing model ready.');
    return { processor, model, config };
  })().catch(error => { ready = null; throw error; });
  return ready;
}

async function guess(image) {
  const { processor, model, config } = await initialize();
  progress('Reading the drawing’s pixels…');
  const bitmap = await createImageBitmap(await (await fetch(image)).blob());
  const side = Math.max(bitmap.width, bitmap.height);
  const square = new OffscreenCanvas(side, side);
  const context = square.getContext('2d');
  context.fillStyle = '#ffffff'; context.fillRect(0, 0, side, side);
  context.drawImage(bitmap, (side - bitmap.width) / 2, (side - bitmap.height) / 2);
  bitmap.close();
  const url = URL.createObjectURL(await square.convertToBlob({ type: 'image/png' }));
  let inputs;
  try { inputs = await processor(await RawImage.fromURL(url)); }
  finally { URL.revokeObjectURL(url); }
  const output = await model(inputs);
  const values = output.image_embeds.data;
  if (values.length !== 512) throw new Error('Unexpected image-vector dimensions.');
  const norm = Math.hypot(...values);
  const imageVector = Float32Array.from(values, value => value / norm);
  const articles = new Map();
  for (let i = 0; i < metadata.candidates.length; i++) {
    let score = 0;
    const offset = i * 512;
    for (let j = 0; j < 512; j++) score += imageVector[j] * textVectors[offset + j];
    const candidate = metadata.candidates[i];
    const previous = articles.get(candidate.doc);
    if (!previous || score > previous.score) articles.set(candidate.doc, {
      doc: candidate.doc, score, candidate,
      vector: Array.from(textVectors.subarray(offset, offset + 512)),
    });
  }
  const ranking = [...articles.values()].sort((a, b) => b.score - a.score || a.doc - b.doc);
  // Reconstruct the actual resized input for the reveal, before normalization.
  const [, channels, height, width] = inputs.pixel_values.dims;
  if (channels !== 3) throw new Error('Unexpected drawing pixel format.');
  const preview = new OffscreenCanvas(width, height);
  const previewContext = preview.getContext('2d');
  const pixels = previewContext.createImageData(width, height);
  const plane = width * height;
  for (let i = 0; i < plane; i++) {
    for (let channel = 0; channel < 3; channel++) {
      pixels.data[i * 4 + channel] = Math.round((inputs.pixel_values.data[channel * plane + i] * config.image_std[channel] + config.image_mean[channel]) * 255);
    }
    pixels.data[i * 4 + 3] = 255;
  }
  previewContext.putImageData(pixels, 0, 0);
  return { ranking, imageVector: Array.from(imageVector), previewBlob: await preview.convertToBlob({ type: 'image/png' }),
    model: metadata.model, revision: metadata.revision, dimensions: 512, imageSize: width,
    patchSize: 32, prototypeCount: metadata.candidates.length };
}

onmessage = async event => {
  const { id, type, image } = event.data;
  try {
    const result = type === 'warm' ? (await initialize(), { ready: true }) : await guess(image);
    postMessage({ id, type: 'result', result });
  } catch (error) { postMessage({ id, type: 'error', error: error.message }); }
};
