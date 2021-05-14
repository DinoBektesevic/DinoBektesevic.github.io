/**
   This file is essentially a copy of the simple plot BUT FOR THE
   FOLLOWING major. important difference:

   1) Note g1 = svg.append("g") comapred to g = svg.append("g")
   This variable becomes globally visible, through some magic,
   and the plots would not work if it was named the same as in
   simpleplot.js because they keep overriding the same values.
   Note how, idiotically, the same exact synthax does not
   result with a problem with appending an SVG element to
   the div.

   2) Classic JS issue of everything is global, so all functions
   must be named differently.

   Also note that in onMouseOut we set the class attribute
   value to .bar1 to have it revert to black (see CSS)
**/


/**
 * Creates a simple plot with a mouse over and mouse out events in a
 * given SVG element.
 * @param  {String} elementid SVG Element ID on which plot is rendered.
 */
function simplePlot2(elementid){
    // <td><svg id="growthplt" width = "500" height = "500"></svg></td>

    //var data = d3.range(0, 2 * Math.PI, .01).map(function(t) {
    //    return [t, Math.sin(2 * t) * Math.cos(2 * t)];
    //});

    var width = 960,
        height = 500,
        radius = Math.min(width, height) / 2 - 30;

    var r = d3.scaleLinear()
        .domain([0, 1])
        .range([0, radius]);

    var theta = d3.scaleLinear().range(0, width);
    //    var r = d3.scaleLinear().range(0, height).domain([0, 1]);

    var line = d3.lineRadial()
        .radius(function(d) { return r(d.r); })
        .angle(function(d) { return d.azRad; });

    var svg = d3.select(elementid).append("svg")
        .attr("width", width)
        .attr("height", height)
        .append("g")
        .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

    var gr = svg.append("g")
        .attr("class", "r axis")
        .selectAll("g")
        .data(r.ticks(5).slice(1))
        .enter().append("g");

    gr.append("circle")
        .attr("r", r);

    gr.append("text")
        .attr("y", function(d) { return -r(d) - 4; })
        .attr("transform", "rotate(15)")
        .style("text-anchor", "middle")
        .text(function(d) { return d; });

    var ga = svg.append("g")
        .attr("class", "a axis")
        .selectAll("g")
        .data(d3.range(0, 360, 30))
        .enter().append("g")
        .attr("transform", function(d) { return "rotate(" + -d + ")"; });

    ga.append("line")
        .attr("x2", radius);

    ga.append("text")
        .attr("x", radius + 6)
        .attr("dy", ".35em")
        .style("text-anchor", function(d) { return d < 270 && d > 90 ? "end" : null; })
        .attr("transform", function(d) { return d < 270 && d > 90 ? "rotate(180 " + (radius + 6) + ",0)" : null; })
        .text(function(d) { return d + "°"; });


    let select = d3.select("body")
        .append("select")
        .attr("id", "button")
        .on("change", function() {
            // Log value it is changed to:
            // console.log(this.value);
            draw(this.value);
        });

    d3.csv("../data/mjd-59418-sdss-simple-expanded-polar.csv").then(function(data) {
        dates = new Set(data.map(function(d){ return d.mjdExpStart;}));
        fields = new Set(data.map(function(d){ return d.mjdExpStart;}));

        // Add the columns as options:
        var options = select.selectAll(null)
            .data(dates.keys())
            .enter()
            .append("option")
            .text(function(d) { return d; });
    });

    var draw = function(fieldid) {

        svg.selectAll("#point").remove();

        d3.csv("../data/mjd-59418-sdss-simple-expanded-polar.csv").then(function(data) {
            filteredData = data.filter(function(d){ return d.mjdExpStart == fieldid; });

            point = svg.selectAll("point")
                .data(filteredData);

            //point = svg.selectAll("point")
            //    .data(filteredData);

            point.enter()
                .append("circle")
                .attr("id", "point")
                .attr("transform", function(d) {
                    // use the line function and parse out the coordinates
                    var coors = line([d]).slice(1).slice(0, -1);
                    return "translate(" + coors + ")";
                })
                .attr("r", 1);
            // svg.selectAll('circle').data(filteredData).exit().remove();
            // svg.selectAll('circle').data(filteredData).exit().remove();
        });
    };

    svg.exit().remove();
};
