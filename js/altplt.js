/**
 * Creates a simple plot with a mouse over and mouse out events in a
 * given SVG element.
 * @param  {String} elementid SVG Element ID on which plot is rendered.
 */

// decide the size of the overall canvas
var margin = {top: 30, right: 20, bottom: 30, left: 50},
    width = 800 - margin.left - margin.right,
    height = 600 - margin.top - margin.bottom;

var pointSize = 4;
var pointColor = "#69b3a2";
var altLowerLimit = 40; // bottom limit of plot in altitude
var altUpperLimit = 90; // top limit of plot in altitude
var yAxisShift = 20/60/24; // 20 minutes in mjds
var svg; // make this a global variable


function makePlot(data){
    // this gets called after the data has been read in
    // first find the range of x axis
    let mjdNightStart = data[0].mjdNightStart - yAxisShift;
    let mjdNightEnd = data[0].mjdNightEnd;

    // set up the x and y axes
    // the start/end times set the scale extent of the x axis
    let x = d3.scaleLinear()
        .domain([mjdNightStart, mjdNightEnd]) // go from beginning to end of night
        .range([margin.left, width - margin.right]);
    // .nice();

    console.log(svg);
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x));
    console.log(svg);
    let y = d3.scaleLinear()
        .domain([altLowerLimit, altUpperLimit])  // go from 0 to 90 degrees altitude
        .range([height, 0]);
    // .nice();

    svg.append("g")
    // use translate to nudge the axes to where they look decent
        .attr("transform", "translate(" + margin.left + ",0)")  // look what happens when you comment/uncomment this
        .call(d3.axisLeft(y));

    // group the data by time bin, this creates a nested list
    // d3.groups() returns an array
    // d3.group() returns a Map, I prefer the array
    let timeGroup = d3.groups(data, d => d.mjdExpStart); // i still don't understand what the => operator does

    let pointGroup = svg.append("g"); // this will hold all the dots

    for (const time of timeGroup){
        // time is in the form [key, array]
        // where key is the mjdExpStart, and array is the
        // list of all fields avaiable at this time
        console.log(time);
        let pointArray = time[1];  // just care about the value, not the key
        // begin plotting dots, one group at a time
        pointGroup
            .selectAll("dot")
            .data(pointArray)
            .enter()
            .append("circle")
                .attr("cx", function (d) {return x(d.mjdExpStart); } )
                .attr("cy", function (d) {return y(d.alt); } )
                .attr("r", pointSize)
                .style("fill", pointColor)
    }
}


function altplt(elementid){
    // this gets called when the page loads
    //first overwrite the gloval variable svg
    // console.log("altplt called");
    svg = d3.select(elementid)
        .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform",
                  "translate(" + margin.left + "," + margin.top + ")");

    // console.log(svg);
    d3.csv("../data/mjd-59310-sdss-simple.csv").then(makePlot);

}


