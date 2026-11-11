import json
import tempfile
import textwrap
from pathlib import Path

import nbformat


notebook_path = Path('pnas_report/notebooks/exploration.ipynb')
original_text = notebook_path.read_text(encoding='utf-8')
notebook = json.loads(original_text)
review_dir = Path(tempfile.mkdtemp(prefix='pnas_visual_review_'))
(review_dir / 'original.ipynb').write_text(original_text, encoding='utf-8')
print(f'Review files: {review_dir}', flush=True)


def markdown(cell_id, source):
    return {'cell_type': 'markdown', 'id': cell_id, 'metadata': {},
            'source': textwrap.dedent(source).strip().splitlines(keepends=True)}


def code(cell_id, source):
    return {'cell_type': 'code', 'id': cell_id, 'metadata': {},
            'execution_count': None, 'outputs': [],
            'source': textwrap.dedent(source).strip().splitlines(keepends=True)}


guide = markdown('visual-reading-guide', '''
    **Prefer pictures?** Run **Run All**, then jump to the
    [visual sanity checks](#visual-sanity-checks) at the end. Start with the
    age difference and shuffled baseline; the following figures explain who
    enters the comparison, what the communities look like, and what changes
    under alternative choices. The original calculations remain above.
''')

visual_cells = [
    markdown('visual-sanity-checks', '''
        <a id="visual-sanity-checks"></a>
        ## Visual sanity checks

        Read one figure at a time. **Blue = under 30; orange = 30+.** Every
        plot below uses the data and results already calculated above.
        Each heading gives the question to ask and the patterns to inspect.

        ### 1. How big is the difference, relative to shuffled ages?

        **Look for:** the distance between the two weighted rates and the
        position of the observed difference in the null distribution. Both
        bars use a full 0–100% scale. The shaded band is the middle 95% of
        **shuffled differences**, not a confidence interval for the effect.
        The orange histogram counts shuffles at least as large as observed.
    '''),
    code('visual-main-result', '''
        from matplotlib.colors import LogNorm
        from matplotlib.lines import Line2D
        from matplotlib.ticker import PercentFormatter, StrMethodFormatter

        UNDER30_COLOR = '#286c8e'
        AGE30PLUS_COLOR = '#c85d35'
        VISUAL_STYLE = {
            'figure.facecolor': 'white', 'axes.facecolor': '#fafbfc',
            'font.size': 10, 'axes.titlesize': 12, 'axes.titleweight': 'bold',
            'axes.labelcolor': '#354354', 'text.color': '#253344',
            'axes.edgecolor': '#cbd3da', 'grid.color': '#e4e9ee',
            'axes.spines.top': False, 'axes.spines.right': False,
            'figure.dpi': 125,
        }

        with plt.rc_context(VISUAL_STYLE):
            fig, axes = plt.subplots(1, 2, figsize=(13, 4.6),
                                     gridspec_kw={'width_ratios': [1, 1.5]}, layout='constrained')
            rates = [primary_result['rate_under30_percent'], primary_result['rate_30plus_percent']]
            axes[0].barh([0, 1], rates, height=0.5, color=[UNDER30_COLOR, AGE30PLUS_COLOR])
            axes[0].set(yticks=[0, 1], yticklabels=[
                f"Under 30\\n{primary_result['n_under30']:,} moves",
                f"30+\\n{primary_result['n_30plus']:,} moves"],
                xlim=(0, 100), xlabel='Overlap-weighted crossing share',
                title='Do the weighted crossing rates differ?')
            axes[0].invert_yaxis()
            axes[0].xaxis.set_major_formatter(PercentFormatter(100))
            for y, rate in enumerate(rates):
                axes[0].text(rate + 1.5, y, f'{rate:.2f}%', va='center', fontweight='bold')

            observed = primary_result['difference_pp']
            upper_tail = primary_null >= observed
            axes[1].axvspan(primary_result['null_2.5_percentile_pp'],
                           primary_result['null_97.5_percentile_pp'],
                           color='#e7edf2', label='Middle 95% of shuffles', zorder=0)
            axes[1].hist([primary_null[~upper_tail], primary_null[upper_tail]],
                         bins=np.histogram_bin_edges(primary_null, bins=32), stacked=True,
                         color=['#9ebccc', AGE30PLUS_COLOR], edgecolor='white', linewidth=0.5,
                         label=['Below observed', 'At least observed'])
            axes[1].axvline(0, color='#687582', linestyle=':', linewidth=1)
            axes[1].axvline(observed, color=AGE30PLUS_COLOR, linewidth=2.2,
                           label=f'Observed: {observed:+.2f} pp')
            axes[1].set(xlabel='30+ minus under 30 (percentage points)',
                        ylabel='Shuffles (count)', title='Is the contrast unusual under shuffled ages?')
            axes[1].text(0.98, 0.97,
                         f"One-sided p = {primary_result['one_sided_p']:.3f}\\n"
                         f'{upper_tail.sum():,} / {len(primary_null):,} shuffles ≥ observed',
                         transform=axes[1].transAxes, ha='right', va='top', fontsize=10,
                         bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': 0.9})
            axes[1].legend(frameon=False, fontsize=8, loc='upper left')
            plt.show()
        display(Markdown(f'**Readout:** {primary_interpretation}'))
    '''),
    markdown('visual-selection-notes', '''
        ### 2. Who is represented in that comparison?

        **Look for:** the largest loss of records on the left, and age or
        season differences in historical endpoint coverage on the right.
        The left-hand bars are **successive subsets of the evaluation window**;
        they do not combine the historical and evaluation branches. Right-hand
        percentages use all evaluation moves in the named age group and season
        as their denominator. The unknown-age record is only in the left panel.
    '''),
    code('visual-sample-selection', '''
        visual_counts = [len(evaluation), len(covered), len(eligible), len(comparison)]
        visual_coverage = (coverage['endpoint_coverage_percent'].unstack('age_group')
                           .reindex(EVALUATION_SEASONS)[['Under 30', '30+']])
        assert all(a >= b for a, b in zip(visual_counts, visual_counts[1:]))

        with plt.rc_context(VISUAL_STYLE):
            fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), layout='constrained')
            axes[0].barh(range(4), visual_counts, height=0.55,
                         color=['#c6d4df', '#9cb9cb', '#769eb5', UNDER30_COLOR])
            axes[0].set(yticks=range(4), yticklabels=[
                'All evaluation moves', 'Both historical\\ncommunities known',
                'Also known age', 'Also both age groups\\nin the origin club-season'],
                xlim=(0, len(evaluation) * 1.49), xlabel='Transfer records (count)',
                title='How much of the evaluation sample remains?')
            axes[0].invert_yaxis()
            axes[0].xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
            for y, count in enumerate(visual_counts):
                axes[0].text(count + len(evaluation) * 0.02, y,
                             f'{count:,}  ({100 * count / len(evaluation):.1f}%)', va='center', fontsize=9)

            x = np.arange(len(EVALUATION_SEASONS))
            for offset, group, color in [(-0.19, 'Under 30', UNDER30_COLOR), (0.19, '30+', AGE30PLUS_COLOR)]:
                bars = axes[1].bar(x + offset, visual_coverage[group], width=0.34, color=color, label=group)
                axes[1].bar_label(bars, labels=[f'{value:.1f}%' for value in visual_coverage[group]],
                                  padding=4, fontsize=9)
            axes[1].set(xticks=x, xticklabels=EVALUATION_SEASONS, ylim=(0, 112),
                        yticks=[0, 25, 50, 75, 100], xlabel='Recorded evaluation season',
                        ylabel='Moves with both historical communities assigned',
                        title='Does endpoint coverage differ by age or season?')
            axes[1].yaxis.set_major_formatter(PercentFormatter(100))
            axes[1].legend(frameon=False, loc='upper left', ncol=2)
            plt.show()
        display(Markdown(
            f"**Readout:** the final comparison retains **{100 * len(comparison) / len(evaluation):.1f}%** "
            f"of evaluation moves. Forming mixed-age club-seasons removes **{len(eligible) - len(comparison):,}** "
            'otherwise age-known, historically covered moves. Check this selection before generalizing the result.'
        ))
    '''),
    markdown('visual-community-notes', '''
        ### 3. Do the historical communities have a sensible structure?

        **Look for:** very uneven community sizes, strong diagonal cells,
        and substantial traffic between particular communities. Labels `C00`,
        `C01`, … are the original community IDs, ordered by size; the example
        club is the member with greatest incoming plus outgoing strength.
        The matrix shows the **largest 20 communities only**, using **logarithmic
        color** so small flows remain visible. White means zero. Rows are origins,
        columns are destinations; diagonal cells are within-community transfers.
        Community fitting and all counts here use historical transfers only.
    '''),
    code('visual-community-structure', '''
        visual_top = community_sizes.head(20)
        visual_flow_communities = flows.assign(
            origin=flows['from_club_id'].map(primary_map),
            destination=flows['to_club_id'].map(primary_map))
        visual_matrix = (visual_flow_communities.pivot_table(
            index='origin', columns='destination', values='weight', aggfunc='sum', fill_value=0)
            .reindex(index=visual_top.index, columns=visual_top.index, fill_value=0))
        visual_community_labels = [
            f"C{group_id:02d} · {club_names.loc[total_strength.loc[sorted(primary_communities[group_id])].idxmax()]}"
            for group_id in visual_top.index]
        visual_within = visual_flow_communities.loc[
            visual_flow_communities['origin'].eq(visual_flow_communities['destination']), 'weight'].sum()

        with plt.rc_context(VISUAL_STYLE):
            fig, axes = plt.subplots(1, 2, figsize=(13, 7), layout='constrained')
            bars = axes[0].barh(range(len(visual_top)), visual_top, color=UNDER30_COLOR, height=0.66)
            axes[0].bar_label(bars, padding=4, fontsize=8)
            axes[0].set(yticks=range(len(visual_top)), yticklabels=visual_community_labels,
                        xlim=(0, visual_top.max() * 1.18), xlabel='Historical clubs (count)',
                        title='Largest communities and an example club')
            axes[0].tick_params(axis='y', labelsize=8.5)
            axes[0].invert_yaxis()

            image = axes[1].imshow(np.ma.masked_equal(visual_matrix.to_numpy(dtype=float), 0),
                                   cmap='Blues', norm=LogNorm(vmin=1, vmax=visual_matrix.to_numpy().max()))
            axes[1].set(xticks=range(len(visual_top)), yticks=range(len(visual_top)),
                        xticklabels=[f'C{i:02d}' for i in visual_top.index],
                        yticklabels=[f'C{i:02d}' for i in visual_top.index],
                        xlabel='Destination community', ylabel='Origin community',
                        title='Directed historical flows between communities')
            axes[1].set_facecolor('white')
            axes[1].tick_params(axis='x', labelrotation=90, labelsize=8)
            axes[1].tick_params(axis='y', labelsize=8)
            fig.colorbar(image, ax=axes[1], shrink=0.65, label='Transfer records (log color scale)')
            plt.show()
        display(Markdown(
            f"**Readout:** these 20 communities contain **{visual_top.sum():,} / {graph.number_of_nodes():,} clubs**. "
            f"The matrix displays **{int(visual_matrix.to_numpy().sum()):,} / {len(historical):,} historical moves** "
            '(both endpoints in the displayed communities). '
            f"Across **all {len(primary_communities)} communities**, "
            f"**{100 * visual_within / len(historical):.1f}%** of historical moves stay within their community. "
            'The diagonal is a diagnostic of the fitted partition, not an independent validation of it.'
        ))
    '''),
    markdown('visual-drivers-notes', '''
        ### 4. Could age imbalance, a single season, or a few clubs drive this?

        **Look for:** changes in the age distribution after selection, sparse
        older-player counts within club-seasons, seasonal sign changes, and
        unusually large contributions from individual club-seasons.
        Age histograms are normalized separately, so their shapes can be compared.
        Seasonal dots reuse the stated overlap weights within that season; they
        are descriptive estimates. Each contribution on the lower right equals
        its club-season's weight share times its age difference. All contributions
        sum to the primary result; only the eight largest absolute ones are shown.
    '''),
    code('visual-result-drivers', '''
        visual_age_bins = np.arange(np.floor(evaluation['age'].min()), np.ceil(evaluation['age'].max()) + 2) - 0.5
        visual_count_labels = ['1', '2', '3–4', '5–9', '10+']
        visual_group_counts = pd.DataFrame({
            group: pd.cut(primary_strata[column], bins=[0, 1, 2, 4, 9, np.inf],
                          labels=visual_count_labels).value_counts(sort=False)
            for group, column in [('Under 30', 'n_under30'), ('30+', 'n_30plus')]})
        visual_seasons = pd.DataFrame([
            {'season': season, 'transfers': int(part['n_total'].sum()), 'weight': part['weight'].sum(),
             'difference_pp': 100 * np.average(part['rate_30plus'] - part['rate_under30'], weights=part['weight'])}
            for season in EVALUATION_SEASONS
            for part in [primary_strata.xs(season, level='transfer_season')]
        ])
        visual_contributions = (100 * (primary_strata['rate_30plus'] - primary_strata['rate_under30'])
                                * primary_strata['weight'] / primary_strata['weight'].sum())
        assert np.isclose(visual_contributions.sum(), primary_result['difference_pp'])
        assert np.isclose(np.average(visual_seasons['difference_pp'], weights=visual_seasons['weight']),
                          primary_result['difference_pp'])
        visual_influential = visual_contributions.loc[visual_contributions.abs().nlargest(8).index].sort_values()

        with plt.rc_context(VISUAL_STYLE):
            fig, axes = plt.subplots(2, 2, figsize=(13, 9.5), layout='constrained')
            for frame, label, color in [(evaluation, 'All evaluation moves with known age', '#93a4b2'),
                                         (comparison, 'Final mixed-age comparison', UNDER30_COLOR)]:
                ages = frame['age'].dropna().to_numpy(dtype=float)
                axes[0, 0].hist(ages, bins=visual_age_bins, weights=np.full(len(ages), 100 / len(ages)),
                                histtype='step', linewidth=2, color=color, label=label)
            axes[0, 0].axvline(30, color=AGE30PLUS_COLOR, linestyle='--', linewidth=1.4, label='Age 30 threshold')
            axes[0, 0].set(xlabel='Age at transfer (years)', ylabel='Share of each sample per one-year bin',
                           title='Does selection change the age distribution?')
            axes[0, 0].yaxis.set_major_formatter(PercentFormatter(100))
            axes[0, 0].legend(frameon=False, fontsize=8)

            x = np.arange(len(visual_count_labels))
            for offset, group, color in [(-0.19, 'Under 30', UNDER30_COLOR), (0.19, '30+', AGE30PLUS_COLOR)]:
                bars = axes[0, 1].bar(x + offset, 100 * visual_group_counts[group] / len(primary_strata),
                                      width=0.34, color=color, label=group)
                axes[0, 1].bar_label(bars, fmt='%.0f%%', padding=3, fontsize=8)
            axes[0, 1].set(xticks=x, xticklabels=visual_count_labels, ylim=(0, 100),
                           xlabel='Transfers per age group in one club-season (count)',
                           ylabel='Share of compared club-seasons', title='How sparse are the within-club age groups?')
            axes[0, 1].yaxis.set_major_formatter(PercentFormatter(100))
            axes[0, 1].legend(frameon=False)

            axes[1, 0].axvline(0, color='#687582', linewidth=1)
            axes[1, 0].axvline(primary_result['difference_pp'], color='#93a4b2', linestyle='--', linewidth=1.3)
            axes[1, 0].scatter(visual_seasons['difference_pp'], range(len(visual_seasons)),
                               s=85, color=AGE30PLUS_COLOR, zorder=3)
            axes[1, 0].set(yticks=range(len(visual_seasons)), yticklabels=[
                f"{row.season}\\n{row.transfers:,} moves" for row in visual_seasons.itertuples()],
                ylim=(len(visual_seasons) - 0.5, -0.5),
                xlim=(min(0, visual_seasons['difference_pp'].min()) - 0.6,
                      max(0, visual_seasons['difference_pp'].max()) + 1),
                xlabel='Weighted 30+ minus under 30 (percentage points)', title='Does the direction persist in each season?')
            for y, value in enumerate(visual_seasons['difference_pp']):
                axes[1, 0].annotate(f'{value:+.2f} pp', (value, y), xytext=(9, 0),
                                    textcoords='offset points', va='center', fontsize=10)
            axes[1, 0].text(0.02, 0.02, 'Dashed line: all seasons combined; dots are descriptive.',
                            transform=axes[1, 0].transAxes, fontsize=8)

            bars = axes[1, 1].barh(range(len(visual_influential)), visual_influential, height=0.62,
                color=[AGE30PLUS_COLOR if value > 0 else UNDER30_COLOR for value in visual_influential])
            axes[1, 1].bar_label(bars, labels=[f'{value:+.3f}' for value in visual_influential], padding=3, fontsize=8)
            axes[1, 1].axvline(0, color='#687582', linewidth=1)
            axes[1, 1].set(yticks=range(len(visual_influential)), yticklabels=[
                f'{club_names.loc[club]} [{club}] · {season}' for club, season in visual_influential.index],
                xlabel='Contribution to the overall difference (percentage points)',
                title='Which club-seasons pull the estimate most?')
            axes[1, 1].tick_params(axis='y', labelsize=8)
            axes[1, 1].margins(x=0.25)
            plt.show()
        visual_one_older = primary_strata['n_30plus'].eq(1)
        display(Markdown(
            f"**Readout:** **{100 * visual_one_older.mean():.1f}%** of compared club-seasons have only one 30+ move. "
            f"They carry **{100 * primary_strata.loc[visual_one_older, 'weight'].sum() / primary_strata['weight'].sum():.1f}%** "
            'of the total overlap weight. The contribution and seasonal averages above both reconcile to the primary difference.'
        ))
    '''),
    markdown('visual-robustness-notes', '''
        ### 5. Does the answer survive reasonable alternative choices?

        **Look for:** a sign change or a large shift in the observed dots.
        Gray segments show the middle 95% of each **permutation null**;
        orange dots show the observed difference. These segments are **not
        effect confidence intervals**. Zero is marked by the vertical line.
        NMI measures agreement with the primary communities (1 = identical).

        The left panel changes communities on the **same transfers**. The right
        panel keeps each player's earliest eligible move before rebuilding
        mixed-age strata, so **both the sample and its club-seasons change**.
        Both panels use the same horizontal scale. Infomap availability is
        reported below the plot, as in the original analysis.
    '''),
    code('visual-robustness', '''
        visual_repeat = pd.DataFrame([primary_result, repeated_result])
        visual_partition_labels = [
            f"{row.method} · {row.settings.replace('; resolution=', ', r=')}\\n"
            f"{row.communities} communities · NMI {row.NMI_to_primary:.3f} · p = {row.one_sided_p:.3f}"
            for row in sensitivity.itertuples()]
        visual_repeat_labels = [
            f"{label}\\n{row.transfers:,} moves · {row.players:,} players · p = {row.one_sided_p:.3f}"
            for label, row in zip(['Primary: all compared moves', 'Earliest eligible move per player'],
                                  visual_repeat.itertuples())]
        visual_all_checks = pd.concat([sensitivity, visual_repeat], ignore_index=True)
        visual_limits = (
            min(0, visual_all_checks['null_2.5_percentile_pp'].min(), visual_all_checks['difference_pp'].min()) - 0.4,
            max(0, visual_all_checks['null_97.5_percentile_pp'].max(), visual_all_checks['difference_pp'].max()) + 1)

        with plt.rc_context(VISUAL_STYLE):
            fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), layout='constrained')
            for ax, frame, labels, title in [
                (axes[0], sensitivity, visual_partition_labels, 'Community boundaries · same sample'),
                (axes[1], visual_repeat, visual_repeat_labels, 'Repeated players · changed sample')]:
                ax.axhspan(-0.35, 0.35, color='#fbede6', zorder=0)
                ax.axvline(0, color='#687582', linewidth=1)
                for y, row in enumerate(frame.itertuples()):
                    ax.plot([frame.iloc[y]['null_2.5_percentile_pp'], frame.iloc[y]['null_97.5_percentile_pp']],
                            [y, y], color='#bac5cf', linewidth=6, solid_capstyle='round', zorder=1)
                    ax.scatter(row.difference_pp, y, color=AGE30PLUS_COLOR, s=85, zorder=3)
                    ax.annotate(f'{row.difference_pp:+.2f} pp', (row.difference_pp, y), xytext=(6, -14),
                                textcoords='offset points', fontsize=9, color=AGE30PLUS_COLOR, fontweight='bold')
                ax.set(yticks=range(len(frame)), yticklabels=labels,
                       ylim=(len(frame) - 0.5, -0.5), xlim=visual_limits,
                       xlabel='30+ minus under 30 (percentage points)', title=title)
                ax.tick_params(axis='y', labelsize=8.5)
                ax.grid(axis='x', alpha=0.5)
            fig.legend(handles=[
                Line2D([0], [0], color='#bac5cf', linewidth=6, label='Middle 95% of shuffled differences (not an effect CI)'),
                Line2D([0], [0], marker='o', linestyle='none', color=AGE30PLUS_COLOR, label='Observed difference')],
                loc='outside lower center', ncol=2, frameon=False, fontsize=9)
            plt.show()
        display(Markdown(f'**Readout:** {boundary_interpretation} {infomap_status}'))
    '''),
]

assert not any(cell.get('id') == 'visual-main-result' for cell in notebook['cells'])
notebook['cells'].insert(1, guide)
if notebook['cells'][-1]['cell_type'] == 'markdown' and not ''.join(notebook['cells'][-1]['source']).strip():
    notebook['cells'].pop()
notebook['cells'].extend(visual_cells)
notebook_path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
nbformat.validate(nbformat.read(notebook_path, as_version=4))
print(f'Added guide and {len(visual_cells)} visual cells; notebook structure valid.', flush=True)
