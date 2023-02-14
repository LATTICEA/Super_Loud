class LineGraph {
  constructor({
    el,
    dates,
    series,
    color,
    maxHeight,
    aspectRatio,
    yLabel,
    formatYTick,
  }) {
    this.el = el;
    this.dates = dates;
    this.series = series;
    this.color = color;
    this.maxHeight = maxHeight;
    this.aspectRatio = aspectRatio;
    this.yLabel = yLabel;
    this.formatYTick = formatYTick;
    this.resize = this.resize.bind(this);
    this.moved = this.moved.bind(this);
    this.left = this.left.bind(this);
    this.init();
  }

  init() {
    this.id = "_" + (this.el.id || crypto.randomUUID());
    this.setup();
    this.scaffold();
    this.wrangle();
    this.addResizeObserver();
  }

  addResizeObserver() {
    if (ResizeObserver) {
      this.ro = new ResizeObserver((entries) => {
        for (const entry of entries) {
          if (entry.contentRect.width > 0) {
            this.resize();
          }
        }
      });
      this.ro.observe(this.el);
    } else {
      window.addEventListener("resize", this.resize);
      this.resize();
    }
  }

  setup() {
    this.margin = {
      top: 40,
      right: 16,
      bottom: 40,
      left: 64,
    };

    this.lineWidth = 5;
    this.focusCircleRadius = 5;

    this.x = d3.scaleTime();
    this.y = d3.scaleLinear();

    this.line = d3
      .line()
      .x((d, i) => this.x(this.dates[i]))
      .y((d) => this.y(d))
      .curve(d3.curveMonotoneX)
      .defined((d) => d !== null);

    this.lineObservedClip = d3
      .area()
      .x((d, i) => this.x(this.dates[i]))
      .y0(0)
      .y1(() => this.height)
      .defined((d) => d === 0);

    this.formatXTick = (d) =>
      d.getMonth() === 0 ? d3.timeFormat("%Y")(d) : d3.timeFormat("Q%q")(d);
  }

  scaffold() {
    this.container = d3.select(this.el).classed("chart", true);
    this.svg = this.container
      .append("svg")
      .on("mousemove", this.moved)
      .on("mouseleave", this.left);
    this.defs = this.svg.append("defs");
    this.gX = this.svg.append("g").attr("class", "axis axis--x");
    this.gY = this.svg.append("g").attr("class", "axis axis--y");
    this.gLines = this.svg
      .append("g")
      .attr("class", "lines-g")
      .attr("clip-path", `url(#${this.id}-clip)`);
    this.gFocus = this.svg.append("g").attr("class", "focus-g");
  }

  wrangle() {
    this.x.domain(d3.extent(this.dates));
    const yExtent = d3.extent(d3.merge(this.series.map((d) => d.values)));
    const yExtentPadding = 0.05 * (yExtent[1] - yExtent[0]);
    const yMin = yExtent[0] - yExtentPadding;
    const yMax = yExtent[1] + yExtentPadding;
    this.y.domain([yMin, yMax]).nice();
  }

  resize() {
    this.width = this.container.node().clientWidth;
    if (this.width === 0) return;
    this.boundedWidth = this.width - this.margin.left - this.margin.right;
    this.height = Math.min(this.maxHeight, this.width * this.aspectRatio);
    this.boundedHeight = this.height - this.margin.top - this.margin.bottom;

    this.x.range([this.margin.left, this.width - this.margin.right]);
    this.y.range([this.height - this.margin.bottom, this.margin.top]);

    this.svg.attr("viewBox", [0, 0, this.width, this.height]);

    this.render();
  }

  render() {
    this.renderXAxis();
    this.renderYAxis();
    this.renderLines();
  }

  renderFocus() {
    this.gFocus
      .selectAll("line")
      .data([0])
      .join((enter) =>
        enter
          .append("line")
          .attr("class", "focus-line")
          .attr("stroke", "currentColor")
          .attr("y1", this.margin.top)
          .attr("y2", this.height - this.margin.bottom)
      );
  }

  renderXAxis() {
    this.gX
      .attr("transform", `translate(0,${this.height - this.margin.bottom})`)
      .call(
        d3
          .axisBottom(this.x)
          .tickPadding(6)
          .tickSizeOuter(0)
          .ticks(this.boundedWidth / 60)
          .tickFormat(this.formatXTick)
      )
      .selectAll(".tick")
      .filter(this.removedXTick)
      .remove();
  }

  renderYAxis() {
    this.gY.attr("transform", `translate(${this.margin.left},0)`).call(
      d3
        .axisLeft(this.y)
        .ticks(this.boundedHeight / 60)
        .tickPadding(12)
        .tickSize(-this.boundedWidth)
        .tickFormat(this.formatYTick)
    );

    this.gY
      .selectAll(".axis-title")
      .data([this.yLabel], (d) => d)
      .join((enter) =>
        enter
          .append("text")
          .attr("class", "axis-title")
          .attr("fill", "currentColor")
          .attr("x", -this.margin.left)
          .attr("y", this.margin.top - 24)
          .attr("text-anchor", "start")
          .text((d) => d)
      );
  }

  renderLines() {
    this.gLines
      .selectAll("clipPath")
      .data(this.series, (d) => d.id)
      .join((enter) =>
        enter
          .append("clipPath")
          .attr("id", (d) => `${this.id}-${d.id}-clip`)
          .call((clipPath) => clipPath.append("path"))
      )
      .select("path")
      .attr("d", (d) => this.lineObservedClip(d.inferred));

    this.gLines
      .selectAll(".line-path--inferred")
      .data(this.series, (d) => d.id)
      .join((enter) =>
        enter
          .append("path")
          .attr("class", "line-path line-path--inferred")
          .attr("fill", "none")
          .attr("stroke", (d) => this.color(d.id))
          .attr("stroke-width", this.lineWidth)
          .attr("stroke-dasharray", `${this.lineWidth} ${this.lineWidth * 2}`)
      )
      .attr("d", (d) => this.line(d.values));

    this.gLines
      .selectAll(".line-path--observed")
      .data(this.series, (d) => d.id)
      .join((enter) =>
        enter
          .append("path")
          .attr("clip-path", (d) => `url(#${this.id}-${d.id}-clip)`)
          .attr("class", "line-path line-path--observed")
          .attr("fill", "none")
          .attr("stroke", (d) => this.color(d.id))
          .attr("stroke-width", this.lineWidth)
      )
      .attr("d", (d) => this.line(d.values));
  }

  updateFocus(iFocus, focusSeries) {
    this.iFocus = iFocus;
    this.focusSeries = focusSeries;

    if (this.iFocus === null) return this.gFocus.style("display", "none");

    this.gFocus
      .style("display", null)
      .attr("transform", `translate(${this.x(this.dates[this.iFocus])},0)`);

    this.gFocus
      .selectAll(".focus-line")
      .data([0])
      .join((enter) =>
        enter
          .append("line")
          .attr("class", "focus-line")
          .attr("y1", this.height - this.margin.bottom)
          .attr("y2", this.margin.top)
          .attr("stroke", "currentColor")
      );

    this.gFocus
      .selectAll(".focus-circle")
      .data(this.focusSeries, (d) => d.id)
      .join((enter) =>
        enter
          .append("circle")
          .attr("class", "focus-circle")
          .attr("fill", (d) => this.color(d.id))
          .attr("r", this.focusCircleRadius)
      )
      .attr("cy", (d) => this.y(d.value));
  }

  moved(event) {
    const [px, py] = d3.pointer(event, this.el);
    const x0 = this.x.invert(px);
    const iFocus = d3.bisectCenter(this.dates, x0);
    if (this.iFocus === iFocus) return;
    this.iFocus = iFocus;
    this.container.dispatch("focuschange", {
      detail: {
        iFocus: this.iFocus,
        pointer: [this.x(this.dates[iFocus]), py],
      },
    });
  }

  left() {
    this.iFocus = null;
    this.container.dispatch("focuschange", {
      detail: {
        iFocus: null,
      },
    });
  }

  update() {
    this.wrangle();
    this.render();
  }
}
