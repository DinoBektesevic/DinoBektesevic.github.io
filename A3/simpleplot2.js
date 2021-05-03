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
    var svg = d3.select(elementid).append("svg")
        .attr("height", 500)
        .attr("width", 500);
		margin = 200;
		width = svg.attr("width") - margin;
		height = svg.attr("height") - margin;

		svg.append("text")
        .attr("transform", "translate(100,0)")
		    .attr("x", 50).attr("y", 50)
		    .attr("font-size", "20px")
		    .attr("class", "title")
		    .text("Population bar chart");

	  x = d3.scaleBand().range([0, width]).padding(0.4);
		y = d3.scaleLinear().range([height, 0]);

		g1 = svg.append("g")
        .attr("transform", "translate(" + 100 + "," + 100 + ")");

		d3.csv("data.csv", function(error, data) {
		    if (error) {
		        throw error;
		    }

		    x.domain(data.map(function(d) { return d.year; }));
		    y.domain([0, d3.max(data, function(d) { return d.population; })]);

		    g1.append("g")
		     .attr("transform", "translate(0," + height + ")")
		     .call(d3.axisBottom(x))
		     .append("text")
		     .attr("y", height - 250)
		     .attr("x", width - 100)
		     .attr("text-anchor", "end")
		     .attr("font-size", "18px")
		     .attr("stroke", "blue").text("year");

		    g1.append("g")
		        .append("text")
		        .attr("transform", "rotate(-90)")
		        .attr("y", 6)
		        .attr("dy", "-5.1em")
		        .attr("text-anchor", "end")
		        .attr("font-size", "18px")
		        .attr("stroke", "blue")
		        .text("population");

		    g1.append("g")
		        .attr("transform", "translate(0, 0)")
		        .call(d3.axisLeft(y));

		    g1.selectAll(".bar1")
		        .data(data)
		        .enter()
		        .append("rect")
		        .attr("class", "bar1")
		        .on("mouseover", simplePlot2OnMouseOver)
		        .on("mouseout", simplePlot2OnMouseOut)
		        .attr("x", function(d) { return x(d.year); })
		        .attr("y", function(d) { return y(d.population); })
		        .attr("width", x.bandwidth()).transition()
		        .ease(d3.easeLinear).duration(200)
		        .delay(function (d, i) {
		            return i * 25;
		        })
		        .attr("height", function(d) { return height - y(d.population); });
		});
};


// I don't know why these functions HAVE TO be defined after we already called them
// but there we go and here we are
/**
 * Event registered when mouse is positioned over the bar in a simple
 * plot. The bar will change color and highlight.
 * @param  {Object} d Rectangle object selected by the cursor.
 * @param  {Number} i Zero based Index of the selected rectangle.
 */
function simplePlot2OnMouseOver(d, i) {
    d3.select(this)
        .attr('class', 'highlight');

    d3.select(this)
        .transition()
        .duration(200)
        .attr('width', x.bandwidth() + 5)
        .attr("y", function(d) { return y(d.population) - 10; })
        .attr("height", function(d) { return height - y(d.population) + 10; });

    g1.append("text")
        .attr('class', 'val')
        .attr('x', function() {
            return x(d.year);
        })
        .attr('y', function() {
            return y(d.population) - 10;
        });
}


/**
 * Event registered when mouse is positioned leves a bar on a simple
 * plot. Color and highlight are reset to original values.
 * @param  {Object} d Rectangle object selected by the cursor.
 * @param  {Number} i Zero based Index of the selected rectangle.
 */
function simplePlot2OnMouseOut(d, i) {

    d3.select(this)
        .attr('class', 'bar1');

    d3.select(this)
        .transition()
        .duration(200)
        .attr('width', x.bandwidth())
        .attr("y", function(d) { return y(d.population); })
        .attr("height", function(d) { return height - y(d.population); });

    d3.selectAll('.val')
        .remove();
}
