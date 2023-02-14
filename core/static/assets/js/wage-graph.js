class WageGraph {
  constructor({ el, data, type }) {
    this.el = el;
    this.data = data;
    this.type = type;
    this.init();
  }

  init() {
    this.id = "_" + (this.el.id || crypto.randomUUID());
    this.wrangle();
    this.setup();
    this.scaffold();
  }

  update() {
    this.wrangle();
    this.updateChart();
  }

  wrangle() {
    const parseDate = d3.timeParse("Q%q-%Y");
    this.data = JSON.parse(JSON.stringify(this.data));
    this.data.dates = this.data.dates.map(parseDate);
    this.data.series = this.data.series.filter((d) =>
      d.values.some((e) => e !== null)
    );

    this.color = d3
      .scaleOrdinal()
      .domain(this.data.series.map((d) => d.id))
      .range(d3.schemeSet2);
  }

  setup() {
    this.maxHeight = 560;
    this.aspectRatio = 1;

    this.formatYTick = d3.format("$,~s");
    this.formatValue = {
      hourly: (d) => `$<span>${d3.format(".2f")(d)}</span>/hour`,
      annually: (d) => `$<span>${d3.format(",")(d)}</span>/year`,
    };
    this.formatDate = d3.timeFormat("Q%q-%Y");

    this.yLabel = "Wage";
  }

  scaffold() {
    d3.select(this.el).selectAll("*").remove();
    this.container = d3
      .select(this.el)
      .append("div")
      .attr("class", "graph wage-graph");
    this.scaffoldControls();
    this.scaffoldChart();
    this.footerContainer = this.container
      .append("div")
      .attr("class", "chart-footer");
    if (this.data.series.length > 1) this.scaffoldLegend();
    this.scaffoldLogo();
    this.scaffoldTooltip();
  }

  scaffoldControls() {
    this.controls = this.container
      .append("div")
      .attr("class", "controls")
      .attr("data-ignore", "");

    this.downloadControlContainer = this.controls.append("div");
    new GraphDownloadControl({
      el: this.downloadControlContainer.node(),
      elDOM: this.container.node(),
    });
  }

  scaffoldChart() {
    this.chartContainer = this.container.append("div");
    this.chart = new LineGraph({
      el: this.chartContainer.node(),
      dates: this.data.dates,
      series: this.data.series,
      color: this.color,
      maxHeight: this.maxHeight,
      aspectRatio: this.aspectRatio,
      yLabel: this.yLabel,
      formatYTick: this.formatYTick,
    });

    this.chartContainer.on("focuschange", (event) => {
      const { iFocus, pointer } = event.detail;

      if (iFocus !== null) {
        const focusSeries = this.chart.series
          .map((d) => ({
            id: d.id,
            name: d.name,
            value: d.values[iFocus],
          }))
          .filter((d) => d.value)
          .sort((a, b) => d3.ascending(a.value, b.value));
        if (focusSeries.length === 0) {
          this.tooltip.hide();
          this.chart.updateFocus(null);
        } else {
          const content = this.getTooltipContent(iFocus, focusSeries);
          this.tooltip.show(content);
          this.tooltip.move(...pointer);
          this.chart.updateFocus(iFocus, focusSeries);
        }
      } else {
        this.tooltip.hide();
        this.chart.updateFocus(null);
      }
    });
  }

  updateChart() {
    this.chart.dates = this.data.dates;
    this.chart.series = this.data.series;
    this.chart.color = this.color;
    this.chart.update();
  }

  scaffoldLegend() {
    this.legendContainer = this.footerContainer
      .append("div")
      .attr("id", `${this.id}-legend`)
      .on("change", () => {
        const selectedIds = this.legend.selected;
        this.chart.series = this.data.series.filter((d) =>
          selectedIds.includes(d.id)
        );
        this.chart.update();
      });
    this.legend = new GraphLegend({
      el: this.legendContainer.node(),
      color: this.color,
      labels: this.data.series.map((d) => d.name),
    });
  }

  scaffoldLogo() {
    this.logoContainer = this.footerContainer.append("div");
    new GraphLogo({
      el: this.logoContainer.node(),
    });
  }

  scaffoldTooltip() {
    this.tooltipContainer = this.chartContainer.append("div");
    this.tooltip = new GraphTooltip({
      el: this.tooltipContainer.node(),
      elBounds: this.chartContainer.node(),
    });
  }

  getTooltipContent(iFocus, focusSeries) {
    return `
      <div class="tip__header">${this.formatDate(this.data.dates[iFocus])}</div>
      <div class="tip__body">
        <table class="tip__items">
          <tbody>
          ${focusSeries
            .slice()
            .reverse()
            .map(
              (d) => `
            <tr class="tip__item">
              <td class="tip__item__swatch"><div style="background-color: ${this.color(
                d.id
              )}"></div></td>
              <td class="tip__item__name">${d.name}</td>
              <td class="tip__item__value"><div>${this.formatValue[this.type](
                d.value
              )}</div></td>
            </tr>
          `
            )
            .join("")}
          </tbody>
        </table>
      </div>
    `;
  }
}