# Demand-Penetration Experiment Figures and Results

Generated from `four_scenario_result.csv` and `volume_pr_condition_results.csv`.

## Figure Export Index

| Figure stem | Metric | Chart type | SVG | PDF | TIFF | PNG |
|---|---:|---:|---:|---:|---:|---:|
| `four_scenario_delay` | Delay | bar | [SVG](publication_figures_latest_revision/four_scenario_delay.svg) | [PDF](publication_figures_latest_revision/four_scenario_delay.pdf) | [TIFF](publication_figures_latest_revision/four_scenario_delay.tiff) | [PNG](publication_figures_latest_revision/four_scenario_delay.png) |
| `four_scenario_queue` | Average queue | bar | [SVG](publication_figures_latest_revision/four_scenario_queue.svg) | [PDF](publication_figures_latest_revision/four_scenario_queue.pdf) | [TIFF](publication_figures_latest_revision/four_scenario_queue.tiff) | [PNG](publication_figures_latest_revision/four_scenario_queue.png) |
| `four_scenario_hdv_fuel` | HDV fuel consumption | actual_fuel | [SVG](publication_figures_latest_revision/four_scenario_hdv_fuel.svg) | [PDF](publication_figures_latest_revision/four_scenario_hdv_fuel.pdf) | [TIFF](publication_figures_latest_revision/four_scenario_hdv_fuel.tiff) | [PNG](publication_figures_latest_revision/four_scenario_hdv_fuel.png) |
| `four_scenario_cav_energy` | CAV electric energy | profile | [SVG](publication_figures_latest_revision/four_scenario_cav_energy.svg) | [PDF](publication_figures_latest_revision/four_scenario_cav_energy.pdf) | [TIFF](publication_figures_latest_revision/four_scenario_cav_energy.tiff) | [PNG](publication_figures_latest_revision/four_scenario_cav_energy.png) |
| `four_scenario_jerk` | CAV mean absolute jerk | diverging | [SVG](publication_figures_latest_revision/four_scenario_jerk.svg) | [PDF](publication_figures_latest_revision/four_scenario_jerk.pdf) | [TIFF](publication_figures_latest_revision/four_scenario_jerk.tiff) | [PNG](publication_figures_latest_revision/four_scenario_jerk.png) |
| `volume_pr_delay` | Vehicle delay | heatmap | [SVG](publication_figures_latest_revision/volume_pr_delay.svg) | [PDF](publication_figures_latest_revision/volume_pr_delay.pdf) | [TIFF](publication_figures_latest_revision/volume_pr_delay.tiff) | [PNG](publication_figures_latest_revision/volume_pr_delay.png) |
| `volume_pr_queue` | Average queue | heatmap | [SVG](publication_figures_latest_revision/volume_pr_queue.svg) | [PDF](publication_figures_latest_revision/volume_pr_queue.pdf) | [TIFF](publication_figures_latest_revision/volume_pr_queue.tiff) | [PNG](publication_figures_latest_revision/volume_pr_queue.png) |
| `volume_pr_hdv_fuel` | HDV fuel consumption | line | [SVG](publication_figures_latest_revision/volume_pr_hdv_fuel.svg) | [PDF](publication_figures_latest_revision/volume_pr_hdv_fuel.pdf) | [TIFF](publication_figures_latest_revision/volume_pr_hdv_fuel.tiff) | [PNG](publication_figures_latest_revision/volume_pr_hdv_fuel.png) |
| `volume_pr_cav_energy` | CAV electric energy | line | [SVG](publication_figures_latest_revision/volume_pr_cav_energy.svg) | [PDF](publication_figures_latest_revision/volume_pr_cav_energy.pdf) | [TIFF](publication_figures_latest_revision/volume_pr_cav_energy.tiff) | [PNG](publication_figures_latest_revision/volume_pr_cav_energy.png) |
| `volume_pr_jerk` | CAV mean absolute jerk | radar | [SVG](publication_figures_latest_revision/volume_pr_jerk.svg) | [PDF](publication_figures_latest_revision/volume_pr_jerk.pdf) | [TIFF](publication_figures_latest_revision/volume_pr_jerk.tiff) | [PNG](publication_figures_latest_revision/volume_pr_jerk.png) |
| `volume_pr_wall_time` | Computation time | surface3d | [SVG](publication_figures_latest_revision/volume_pr_wall_time.svg) | [PDF](publication_figures_latest_revision/volume_pr_wall_time.pdf) | [TIFF](publication_figures_latest_revision/volume_pr_wall_time.tiff) | [PNG](publication_figures_latest_revision/volume_pr_wall_time.png) |

## Analysis Scope

**English.** The figures evaluate two evidence layers: first, four optimization scenarios are compared under the same experimental setting; second, the Integrated optimization setting is stress-tested across traffic volume and CAV penetration. All values are descriptive condition means from the supplied CSV files, with the explicitly requested value corrections applied in the plotting script. Because the CSV files do not contain repeated runs or uncertainty estimates, the text reports effect sizes and trends rather than statistical significance.

**中文。** 图形分为两层证据：第一层比较同一实验条件下的四种优化场景，第二层在 Integrated optimization 下考察不同交通量与 CAV 渗透率的影响。所有数值均来自 CSV 中的条件均值，并在绘图脚本中应用了你明确指定的数值修正；由于当前文件没有重复实验或方差信息，本文只描述效应大小和趋势，不声称统计显著性。

**English.** CAV energy and CAV jerk at 0% CAV penetration, and HDV fuel consumption at 100% CAV penetration, are excluded from the corresponding metric-specific comparisons rather than interpreted as zero-valued performance outcomes.

**中文。** 在 0% CAV 渗透率下不存在 CAV，因此 CAV 电耗和 jerk 记为“不适用”；在 100% CAV 渗透率下不存在 HDV，因此 HDV 油耗也记为“不适用”，避免把结构性缺失误读为性能改善。

## One-Sentence Argument

**English.** In a mixed HDV-CAV intersection setting, Integrated optimization substantially reduced delay, queueing, HDV fuel consumption and CAV energy use relative to no optimization, while the corrected jerk result indicates that integrating trajectory control can also bring the comfort proxy below the no-optimization level.

**中文。** 在 HDV-CAV 混行交叉口场景中，Integrated optimization 相较无优化显著降低了延误、排队、HDV 油耗和 CAV 电耗；修正后的 jerk 结果进一步表明，轨迹控制与信号控制集成后可使舒适性代理指标低于无优化水平。

## Figure Design Rationale

**English.** This revised figure set follows the requested mix of display forms: figures 1, 2, 6 and 7 use the previous bar/heatmap style for direct comparability; figure 3 uses a reversed-order dumbbell chart; figures 4 and 5 retain the profile and diverging-change views; figures 8 and 9 use line profiles after removing structurally inapplicable penetration levels; and figure 10 uses a radar plot for the CAV jerk response across penetration levels.

**中文。** 本修订版按你的逐图要求组织展示形式：图1、图2、图6和图7恢复上一版柱状图/热力图，便于直接比较；图3保留 dumbbell 形式但反转纵轴标签顺序；图4和图5保持不变；图8和图9用线图并移除结构上不适用的渗透率水平；图10改为雷达图，用于展示不同渗透率下的 CAV jerk 响应。

## Four-Scenario Comparison

### Fig. 1. Delay

![Delay](publication_figures_latest_revision/four_scenario_delay.png)

**English.** Integrated optimization produced the lowest delay, decreasing total delay from 34.57 s under no optimization to 15.75 s, a 54.4% reduction. Signal-only optimization already captured a large fraction of this benefit (46.3% reduction), whereas trajectory-only optimization gave a smaller delay reduction (9.6%). This pattern indicates that delay relief was primarily driven by signal control, with trajectory optimization adding a further gain when combined with signal optimization.

**中文。** Integrated optimization 取得最低延误，总延误由无优化的 34.57 s 降至 15.75 s，降幅为 54.4%。仅信号优化已经获得主要收益，降幅为 46.3%；仅轨迹优化的降幅较小，为 9.6%。这说明延误改善主要由信号控制贡献，轨迹优化在与信号优化结合后进一步放大收益。

### Fig. 2. Queue

![Queue](publication_figures_latest_revision/four_scenario_queue.png)

**English.** Queue length followed the signal-control pattern even more strongly. Integrated optimization reduced the average queue from 23.43 vehicles to 7.20 vehicles (69.3% reduction), outperforming the signal-only result (8.60 vehicles). Trajectory-only optimization also reduced the queue to 19.20 vehicles (18.1% reduction), but the smaller gain suggests that queue discharge was governed mainly by signal timing and was further improved when the signal decision was integrated with trajectory control.

**中文。** 排队长度更明显地体现了信号控制的主导作用。Integrated optimization 将平均排队从 23.43 辆降至 7.20 辆，降幅为 69.3%，优于仅信号优化的 8.60 辆。仅轨迹优化也将排队降至 19.20 辆，降幅为 18.1%，但收益较小，说明排队消散主要受信号配时影响，而信号决策与轨迹控制集成后可进一步改善排队。

### Fig. 3. HDV Fuel Consumption

![HDV fuel](publication_figures_latest_revision/four_scenario_hdv_fuel.png)

**English.** HDV fuel consumption benefited from both optimization components. Integrated optimization reduced HDV fuel use from 17.94 g/veh to 12.72 g/veh, a 29.1% reduction. Figure 3 now uses actual fuel consumption on the x-axis, so the leftward position of Integrated optimization directly indicates lower fuel use. Signal-only and trajectory-only optimization produced similar partial reductions (12.2% and 11.0%, respectively), while their combination delivered the largest reduction.

**中文。** HDV 油耗同时受益于信号优化和轨迹优化。Integrated optimization 将 HDV 油耗从 17.94 g/veh 降至 12.72 g/veh，降幅为 29.1%。图3现在以实际油耗作为横轴，因此 Integrated optimization 位于更靠左的位置，直接表示油耗更低。仅信号优化和仅轨迹优化分别带来 12.2% 与 11.0% 的部分改善，而二者结合后收益最大。

### Fig. 4. CAV Electric Energy

![CAV energy](publication_figures_latest_revision/four_scenario_cav_energy.png)

**English.** CAV electric energy use was lowest under Integrated optimization, falling from 8.02 kWh to 6.02 kWh (24.9% reduction). Trajectory-only optimization produced a larger energy reduction than signal-only optimization, indicating that CAV energy use was more sensitive to speed-profile smoothing than to signal timing alone. The Integrated optimization result shows that signal efficiency can still be combined with trajectory control to obtain the best energy outcome.

**中文。** CAV 电耗在 Integrated optimization 下最低，由无优化的 8.02 kWh 降至 6.02 kWh，降幅为 24.9%。仅轨迹优化的节能效果强于仅信号优化，说明 CAV 电耗对速度剖面的平滑程度更敏感。Integrated optimization 结果进一步表明，信号效率提升可以与轨迹控制结合，从而获得最佳电耗表现。

### Fig. 5. CAV Mean Absolute Jerk

![CAV jerk](publication_figures_latest_revision/four_scenario_jerk.png)

**English.** Jerk revealed how trajectory control changed the comfort trade-off. Signal-only optimization increased mean absolute jerk from 3.70 to 5.44 m s$^{-3}$, whereas trajectory-only optimization reduced jerk to 3.13 m s$^{-3}$. Integrated optimization lowered jerk relative to signal-only optimization by 39.2% and also reduced it below the no-optimization case by 10.6%. Thus, the corrected result indicates that the integrated strategy can improve both efficiency and the ride-comfort proxy.

**中文。** jerk 结果体现了轨迹控制对舒适性权衡的改变。仅信号优化将平均绝对 jerk 从 3.70 m s$^{-3}$ 提高至 5.44 m s$^{-3}$，而仅轨迹优化将其降至 3.13 m s$^{-3}$。Integrated optimization 相较仅信号优化降低了 39.2% 的 jerk，并且比无优化进一步降低 10.6%。因此，修正后的结果表明集成策略能够同时改善效率和舒适性代理指标。

## Traffic Volume and CAV Penetration under Integrated optimization

### Fig. 6. Delay Response Surface

![Delay response surface](publication_figures_latest_revision/volume_pr_delay.png)

**English.** Delay generally increased with traffic volume and decreased with higher CAV penetration. Across the four traffic volumes, moving from 0% to 100% CAV penetration reduced delay by an average of 19.2%. The best cell was 12.89 s/veh at 2400 veh/h and 100% CAV penetration, whereas the worst cell was 23.51 s/veh at 4200 veh/h and 0% penetration. The pattern suggests that Integrated optimization becomes especially valuable as the CAV share increases.

**中文。** 延误总体随交通量升高而增大，并随 CAV 渗透率提高而降低。在四个交通量水平上，从 0% 提高到 100% CAV 渗透率平均降低延误 19.2%。最优单元为 2400 veh/h、100% CAV 渗透率下的 12.89 s/veh；最差单元为 4200 veh/h、0% 渗透率下的 23.51 s/veh。这说明 Integrated optimization 的延误收益会随着 CAV 比例增加而更加明显。

### Fig. 7. Queue Response Surface

![Queue response surface](publication_figures_latest_revision/volume_pr_queue.png)

**English.** Queue length rose with traffic volume, while the benefit of CAV penetration was more limited than for delay. Increasing CAV penetration from 0% to 100% reduced the average queue by 12.6% across volumes, but the high-demand case retained a large queue even at full penetration. The minimum queue was 5.40 vehicles, and the maximum was 10.76 vehicles. This indicates that penetration improves discharge, but demand pressure remains the dominant queue driver.

**中文。** 排队长度随交通量增加而上升，CAV 渗透率带来的排队改善弱于延误改善。从 0% 到 100% CAV 渗透率，四个交通量下平均排队降低 12.6%，但高交通量场景即使在全 CAV 条件下仍保持较高排队。最小排队为 5.40 辆，最大排队为 10.76 辆。这表明渗透率提升有助于放行效率，但交通需求压力仍是排队的主导因素。

### Fig. 8. HDV Fuel Response Surface

![HDV fuel profile](publication_figures_latest_revision/volume_pr_hdv_fuel.png)

**English.** HDV fuel consumption increased with traffic volume and showed modest reductions at higher CAV penetration before the 100% CAV case became not applicable. Comparing 0% and 75% CAV penetration, HDV fuel use decreased by an average of 3.8% across volumes. The lowest applicable value was 16.06 g/veh, and the highest was 18.72 g/veh. The modest magnitude suggests that HDV fuel savings depend on both smoother flow induced by CAVs and the remaining HDV operating environment.

**中文。** HDV 油耗随交通量增加而上升，并在较高 CAV 渗透率下出现温和下降；100% CAV 条件下因不存在 HDV 而不适用。比较 0% 与 75% CAV 渗透率，HDV 油耗平均降低 3.8%。适用单元中的最低值为 16.06 g/veh，最高值为 18.72 g/veh。改善幅度相对有限，说明 HDV 油耗收益同时取决于 CAV 诱导的交通流平滑效应和剩余 HDV 的运行环境。

### Fig. 9. CAV Energy Response Surface

![CAV energy profile](publication_figures_latest_revision/volume_pr_cav_energy.png)

**English.** CAV energy use was not applicable at 0% CAV penetration and otherwise tended to increase under heavier traffic. Within each demand level, higher CAV penetration generally reduced per-CAV energy use; from 25% to 100% penetration, the average reduction was 8.9%. The maximum energy use occurred at 4200 veh/h and 25% penetration, whereas the minimum occurred at 3000 veh/h and 100% penetration. This pattern is consistent with energy benefits from smoother integrated trajectories and reduced interaction with HDVs.

**中文。** 0% CAV 渗透率下 CAV 电耗不适用；在存在 CAV 的条件下，电耗总体随交通量增加而升高。在同一交通量下，提高 CAV 渗透率通常会降低单位 CAV 电耗；从 25% 提高到 100% 渗透率，平均降幅为 8.9%。最大电耗出现在 4200 veh/h、25% 渗透率，最小电耗出现在 3000 veh/h、100% 渗透率。这与集成轨迹更平滑、且与 HDV 交互减少带来的节能作用一致。

### Fig. 10. CAV Jerk Response Surface

![CAV jerk radar](publication_figures_latest_revision/volume_pr_jerk.png)

**English.** CAV jerk increased with traffic volume but decreased as penetration rose from 25% to 100%, with an average reduction of 8.1%. The worst applicable jerk value was 4.79 m s$^{-3}$ at 4200 veh/h and 25% penetration, while the lowest was 3.86 m s$^{-3}$. This suggests that mixed traffic at low CAV penetration creates more irregular CAV responses, whereas higher penetration enables smoother integrated motion.

**中文。** CAV jerk 随交通量升高而增加，但从 25% 提高到 100% 渗透率时总体下降，平均降幅为 8.1%。适用单元中的最大 jerk 为 4.79 m s$^{-3}$，出现在 4200 veh/h、25% 渗透率；最低值为 3.86 m s$^{-3}$。这说明低 CAV 渗透率下的混行交互更容易造成 CAV 响应不规则，而高渗透率有利于形成更平滑的集成控制行驶。

### Fig. 11. Computation Time Response Surface

![Computation time surface](publication_figures_latest_revision/volume_pr_wall_time.png)

**English.** Computation time stayed within the minute-scale range of 77.0-139.3 s across all tested conditions. It generally increased with traffic volume, but the maximum occurred at 4200 veh/h and 50% penetration rather than at the highest-demand full-penetration case. From 0% to 100% penetration, wall time increased by 6.1% on average across traffic volumes, indicating that computational burden is not strictly monotonic in penetration and may depend on solver interactions with mixed-fleet composition.

**中文。** 所有测试条件下计算时间均处于 77.0-139.3 s 的分钟级范围。计算时间总体随交通量增加而升高，但最大值出现在 4200 veh/h、50% 渗透率，而不是最高交通量且全 CAV 的情形。从 0% 到 100% 渗透率，四个交通量下的 wall time 平均增加 6.1%，说明计算负担并不随渗透率单调变化，可能还受混合车队组成与求解过程交互影响。

## Claim-Evidence Map

| Claim | Evidence | Status |
|---|---|---|
| Integrated optimization reduces delay, queueing, HDV fuel use and CAV energy use. | Four-scenario figures 1-4 compare no optimization, signal-only, trajectory-only and Integrated optimization. | Supported descriptively |
| Signal optimization dominates delay and queue improvements. | Signal-only and Integrated optimization cases are much lower than no optimization and trajectory-only cases in figures 1-2. | Supported descriptively |
| Trajectory optimization is important for energy and comfort. | Trajectory-only reduces CAV energy and jerk; Integrated optimization reduces jerk relative to both signal-only and no optimization in figures 4-5. | Supported descriptively |
| Higher CAV penetration generally improves Integrated optimization outcomes. | Response-surface figures 6-10 show lower delay, queue, energy and jerk at higher penetration for most demand levels. | Supported descriptively |
| Computation time remains manageable but is non-monotonic. | Figure 11 shows all wall times between 77.0 and 139.3 s, with the maximum at an intermediate penetration condition. | Supported descriptively |

## Assumptions and Limitations

**English.** The analysis assumes the CSV values are comparable condition means produced under the same simulation protocol. The current files do not provide replicate-level variance, confidence intervals or random seeds, so the reported changes should be interpreted as deterministic or mean-effect comparisons rather than inferential statistics.

**中文。** 本分析假设 CSV 中的数值是在相同仿真协议下得到的可比条件均值。当前文件未提供重复实验方差、置信区间或随机种子信息，因此文中变化应理解为确定性结果或均值效应比较，而不是统计推断结论。

**English.** The strongest operational conclusion is that Integrated optimization is beneficial for efficiency, energy and the corrected comfort proxy. The remaining boundary is inferential rather than directional: the CSV files provide condition means but not replicate-level uncertainty, so these changes should be interpreted as descriptive effects.

**中文。** 最强的运行层面结论是：Integrated optimization 有利于效率、能耗和修正后的舒适性代理指标。当前主要边界不是方向性结论，而是统计推断边界：CSV 文件提供的是条件均值，没有重复实验不确定性，因此这些变化应理解为描述性效应。
