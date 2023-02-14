class WageUnemploymentGraph {
  constructor({ el, data, type }) {
    this.el = el;
    this.data = data;
    this.type = type;
    this.init();
  }

  init() {
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

    this.color = d3
      .scaleOrdinal()
      .domain(
        // [this.data.wageSeries, this.data.unemploymentSeries].map((d) => d.name)
        [
            this.data.wageSeries
            , this.data.unemploymentSeries
            , this.data.unemploymentCountSeries
            , this.data.employmentSeries
            , this.data.laborForceSeries
        ].map((d) => d.id)
      )
      .range(d3.schemeSet2);
  }

  setup() {
    // this.maxHeight = 280;
    // this.aspectRatio = 0.5;
    this.maxHeight = 180;
    this.aspectRatio = 1.0;

    this.formatWageYTick = d3.format("$,~s");
    this.formatUnemploymentYTick = d3.format("~%");


    this.formatUnemploymentCountYTick = d3.format(",");
    this.formatEmploymentYTick = d3.format(",");
    this.formatLaborForceYTick = d3.format(",");


    this.formatWageValue = {
      hourly: (d) => `$<span>${d3.format(".2f")(d)}</span>/hour`,
      annually: (d) => `$<span>${d3.format(",")(d)}</span>/year`,
    };
    this.formatUnemploymentValue = (d) =>
      `<span>${d3.format("~")(d * 100)}%</span>`;


    this.formatUnemploymentCountValue = (d) => `<span>${d3.format(",")(d)}</span>`;
    this.formatEmploymentValue = (d) => `<span>${d3.format(",")(d)}</span>`;
    this.formatLaborForceValue = (d) => `<span>${d3.format(",")(d)}</span>`;


    this.formatDate = d3.timeFormat("Q%q-%Y");

    this.wageYLabel = "Wage";
    this.unemploymentYLabel = "Unemployment Rate";
    this.unemploymentCountYLabel = "Unemployment";
    this.employmentYLabel = "Employment";
    this.laborForceYLabel = "Labor Force";
  }

  scaffold() {
    d3.select(this.el).selectAll("*").remove();
    this.container = d3
      .select(this.el)
      .append("div")
      .attr("class", "graph wage-unemployment-graph");
    this.scaffoldControls();
    this.scaffoldChart();
    this.footerContainer = this.container
      .append("div")
      .attr("class", "chart-footer");
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

    this.wageChart = new LineGraph({
      el: this.chartContainer.node(),
      dates: this.data.dates,
      series: [this.data.wageSeries],
      color: this.color,
      maxHeight: this.maxHeight,
      aspectRatio: this.aspectRatio,
      yLabel: this.wageYLabel,
      formatYTick: this.formatWageYTick,
    });
    this.laborForceChart = new LineGraph({
      el: this.chartContainer.node(),
      dates: this.data.dates,
      series: [this.data.laborForceSeries],
      color: this.color,
      maxHeight: this.maxHeight,
      aspectRatio: this.aspectRatio,
      yLabel: this.laborForceYLabel,
      formatYTick: this.formatLaborForceYTick,
    });
    this.employmentChart = new LineGraph({
      el: this.chartContainer.node(),
      dates: this.data.dates,
      series: [this.data.employmentSeries],
      color: this.color,
      maxHeight: this.maxHeight,
      aspectRatio: this.aspectRatio,
      yLabel: this.employmentYLabel,
      formatYTick: this.formatEmploymentYTick,
    });
    this.unemploymentCountChart = new LineGraph({
      el: this.chartContainer.node(),
      dates: this.data.dates,
      series: [this.data.unemploymentCountSeries],
      color: this.color,
      maxHeight: this.maxHeight,
      aspectRatio: this.aspectRatio,
      yLabel: this.unemploymentCountYLabel,
      formatYTick: this.formatUnemploymentCountYTick,
    });
    this.unemploymentChart = new LineGraph({
      el: this.chartContainer.node(),
      dates: this.data.dates,
      series: [this.data.unemploymentSeries],
      color: this.color,
      maxHeight: this.maxHeight,
      aspectRatio: this.aspectRatio,
      yLabel: this.unemploymentYLabel,
      formatYTick: this.formatUnemploymentYTick,
    });



    this.chartContainer.on("focuschange", (event) => {
      const { iFocus, pointer } = event.detail;

      if (iFocus !== null) {
        const wageFocusSeries = [this.data.wageSeries]
          .map((d) => ({
            id: d.id,
            name: d.name,
            value: d.values[iFocus],
          }))
          .filter((d) => d.value)
          .sort((a, b) => d3.ascending(a.value, b.value));
        const unemploymentFocusSeries = [this.data.unemploymentSeries]
          .map((d) => ({
            id: d.id,
            name: d.name,
            value: d.values[iFocus],
          }))
          .filter((d) => d.value)
          .sort((a, b) => d3.ascending(a.value, b.value));


        const unemploymentCountFocusSeries = [this.data.unemploymentCountSeries]
          .map((d) => ({
            id: d.id,
            name: d.name,
            value: d.values[iFocus],
          }))
          .filter((d) => d.value)
          .sort((a, b) => d3.ascending(a.value, b.value));
        const employmentFocusSeries = [this.data.employmentSeries]
          .map((d) => ({
            id: d.id,
            name: d.name,
            value: d.values[iFocus],
          }))
          .filter((d) => d.value)
          .sort((a, b) => d3.ascending(a.value, b.value));
        const laborForceFocusSeries = [this.data.laborForceSeries]
          .map((d) => ({
            id: d.id,
            name: d.name,
            value: d.values[iFocus],
          }))
          .filter((d) => d.value)
          .sort((a, b) => d3.ascending(a.value, b.value));


        // if (wageFocusSeries.length + unemploymentFocusSeries.length === 0) {
        if (
            wageFocusSeries.length 
            + unemploymentFocusSeries.length 
            + unemploymentCountFocusSeries.length 
            + employmentFocusSeries.length 
            + laborForceFocusSeries.length 
            === 0) {
          this.tooltip.hide();
          this.wageChart.updateFocus(null);
          this.unemploymentChart.updateFocus(null);


          this.unemploymentCountChart.updateFocus(null);
          this.employmentChart.updateFocus(null);
          this.laborForceChart.updateFocus(null);


        } else {
          const content = this.getTooltipContent(
            iFocus,
            wageFocusSeries,
            unemploymentFocusSeries,


            unemploymentCountFocusSeries,
            employmentFocusSeries,
            laborForceFocusSeries

          );
          this.tooltip.show(content);
          this.tooltip.move(...pointer);
          this.wageChart.updateFocus(iFocus, wageFocusSeries);
          this.unemploymentChart.updateFocus(iFocus, unemploymentFocusSeries);


          this.unemploymentCountChart.updateFocus(iFocus, unemploymentCountFocusSeries);
          this.employmentChart.updateFocus(iFocus, employmentFocusSeries);
          this.laborForceChart.updateFocus(iFocus, laborForceFocusSeries);


        }
      } else {
        this.tooltip.hide();
        this.wageChart.updateFocus(null);
        this.unemploymentChart.updateFocus(null);


        this.unemploymentCountChart.updateFocus(null);
        this.employmentChart.updateFocus(null);
        this.laborForceChart.updateFocus(null);


      }
    });
  }

  updateChart() {
    this.wageChart.dates = this.data.dates;
    this.wageChart.series = [this.data.wageSeries];
    this.wageChart.update();
    this.unemploymentChart.dates = this.data.dates;
    this.unemploymentChart.series = [this.data.unemploymentSeries];
    this.unemploymentChart.update();


    this.unemploymentCountChart.dates = this.data.dates;
    this.unemploymentCountChart.series = [this.data.unemploymentCountSeries];
    this.unemploymentCountChart.update();

    this.employmentChart.dates = this.data.dates;
    this.employmentChart.series = [this.data.employmentSeries];
    this.employmentChart.update();
    this.laborForceChart.dates = this.data.dates;
    this.laborForceChart.series = [this.data.laborForceSeries];
    this.laborForceChart.update();
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

  getTooltipContent(
      iFocus
      , wageFocusSeries
      , unemploymentFocusSeries
      , unemploymentCountFocusSeries
      , employmentFocusSeries
      , laborForceFocusSeries
  ) {
    return `
      <div class="tip__header">${this.formatDate(this.data.dates[iFocus])}</div>
      <div class="tip__body">
        <table class="tip__items">
          <tbody>
          ${wageFocusSeries
            .map(
              (d) => `
            <tr class="tip__item">
              <td class="tip__item__swatch"><div style="background-color: ${this.color(
                d.id
              )}"></div></td>
              <td class="tip__item__name">${d.name}</td>
              <td class="tip__item__value" align="right"><div>${this.formatWageValue[
                this.type
              ](d.value)}</div></td>
            </tr>
          `
            )
            .join("")}

             ${laborForceFocusSeries
               .map(
                 (d) => `
            <tr class="tip__item">
              <td class="tip__item__swatch"><div style="background-color: ${this.color(
                d.id
              )}"></div></td>
              <td class="tip__item__name">${d.name}</td>
              <td class="tip__item__value" align="right"><div>${this.formatLaborForceValue(
                d.value
              )}</div></td>
            </tr>
          `
               )
               .join("")}

             ${employmentFocusSeries
               .map(
                 (d) => `
            <tr class="tip__item">
              <td class="tip__item__swatch"><div style="background-color: ${this.color(
                d.id
              )}"></div></td>
              <td class="tip__item__name">${d.name}</td>
              <td class="tip__item__value" align="right"><div>${this.formatEmploymentValue(
                d.value
              )}</div></td>
            </tr>
          `
               )
               .join("")}

             ${unemploymentCountFocusSeries
               .map(
                 (d) => `
            <tr class="tip__item">
              <td class="tip__item__swatch"><div style="background-color: ${this.color(
                d.id
              )}"></div></td>
              <td class="tip__item__name">${d.name}</td>
              <td class="tip__item__value" align="right"><div>${this.formatUnemploymentCountValue(
                d.value
              )}</div></td>
            </tr>
          `
               )
               .join("")}

             ${unemploymentFocusSeries
               .map(
                 (d) => `
            <tr class="tip__item">
              <td class="tip__item__swatch"><div style="background-color: ${this.color(
                d.id
              )}"></div></td>
              <td class="tip__item__name">${d.name}</td>
              <td class="tip__item__value" align="right"><div>${this.formatUnemploymentValue(
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
