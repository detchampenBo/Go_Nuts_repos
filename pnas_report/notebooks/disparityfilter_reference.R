# Vertex indices are deliberately numeric and the graph has no name attribute.
reference_backbone <- function(club_ids, routes, alpha) {
    empty <- data.frame(
        from_club_id = integer(), to_club_id = integer(), transfer_count = integer()
    )
    stopifnot(!anyDuplicated(club_ids))
    if (nrow(routes) == 0L) return(list(routes = empty, raw_rows = 0L))

    endpoints <- cbind(
        match(routes$from_club_id, club_ids), match(routes$to_club_id, club_ids)
    )
    stopifnot(!anyNA(endpoints), !anyDuplicated(endpoints))
    graph <- igraph::make_empty_graph(n = length(club_ids), directed = TRUE)
    graph <- igraph::add_edges(graph, as.vector(t(endpoints)),
                              attr = list(weight = routes$transfer_count))
    edge_order <- igraph::as_edgelist(graph, names = FALSE)
    weights <- igraph::edge_attr(graph, "weight", index = igraph::E(graph))
    stopifnot(igraph::is_directed(graph), !("name" %in% igraph::vertex_attr_names(graph)))
    stopifnot(
        all(club_ids[edge_order[, 1]] == routes$from_club_id),
        all(club_ids[edge_order[, 2]] == routes$to_club_id),
        all(weights == routes$transfer_count)
    )

    result <- disparityfilter::backbone(graph, weights = weights, directed = TRUE, alpha = alpha)
    keys <- function(from, to) paste(from, to, sep = ":")
    rows <- match(keys(result$from, result$to), keys(edge_order[, 1], edge_order[, 2]))
    stopifnot(!anyNA(rows), all(result$weight == weights[rows]))
    list(routes = routes[unique(rows), names(empty), drop = FALSE], raw_rows = nrow(result))
}

if (sys.nframe() == 0L) {
    args <- commandArgs(trailingOnly = TRUE)
    stopifnot(length(args) == 2L, packageVersion("disparityfilter") == "2.2.3")
    folder <- args[[1]]
    alphas <- as.numeric(strsplit(args[[2]], ",", fixed = TRUE)[[1]])
    vertices <- read.csv(file.path(folder, "vertices.csv"), colClasses = c("character", "integer", "integer"))
    routes <- read.csv(file.path(folder, "routes.csv"), colClasses = c("character", "integer", "integer", "integer"))
    retained <- list()
    diagnostics <- list()
    for (scope in unique(vertices$scope)) {
        mapping <- vertices[vertices$scope == scope, ]
        stopifnot(identical(mapping$vertex_index, seq_len(nrow(mapping))))
        input <- routes[routes$scope == scope, ]
        for (alpha in alphas) {
            result <- reference_backbone(mapping$club_id, input, alpha)
            for (column in c("scope", "alpha")) {
                value <- if (column == "scope") scope else alpha
                result$routes[[column]] <- rep(value, nrow(result$routes))
            }
            retained[[length(retained) + 1L]] <- result$routes
            diagnostics[[length(diagnostics) + 1L]] <- data.frame(
                scope = scope, alpha = alpha, raw_rows = result$raw_rows
            )
        }
    }
    write.csv(do.call(rbind, retained), file.path(folder, "retained.csv"), row.names = FALSE)
    write.csv(do.call(rbind, diagnostics), file.path(folder, "diagnostics.csv"), row.names = FALSE)
    writeLines(c(R.version.string, as.character(packageVersion("igraph")),
                 as.character(packageVersion("disparityfilter"))), file.path(folder, "versions.txt"))
}
