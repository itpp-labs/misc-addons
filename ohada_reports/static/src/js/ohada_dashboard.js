odoo.define('hrms_dashboard.Dashboard', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var ajax = require('web.ajax');
var ControlPanelMixin = require('web.ControlPanelMixin');
var core = require('web.core');
var rpc = require('web.rpc');
var session = require('web.session');
var web_client = require('web.web_client');

var _t = core._t;
var QWeb = core.qweb;

var OhadaDashboard = AbstractAction.extend(ControlPanelMixin, {
    template: 'OhadaDashboardMain',
    cssLibs: [
        '/web/static/lib/nvd3/nv.d3.css'
    ],
    jsLibs: [
        '/web/static/lib/nvd3/d3.v3.js',
        '/web/static/lib/nvd3/nv.d3.js',
        '/web/static/src/js/libs/nvd3.js'
    ],
    events: {
        'click .approve': 'to_approve',
    },

    init: function(parent, context) {
        this._super(parent, context);
        this.dashboards_templates = ['ManagerDashboard'];
    },

    willStart: function() {
        var self = this;
        return $.when(ajax.loadLibs(this), this._super()).then(function() {
            return self.fetch_data();
        });
    },

    start: function() {
        var self = this;
        this.set("title", 'Dashboard');
        return this._super().then(function() {
            self.render_dashboards();
            self.render_graphs();
            self.$el.parent().addClass('oe_background_grey');
        });
    },

    fetch_data: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'ohada.financial.html.report',
                method: 'get_link',
        }).done(function(result) {
            self.link_ids =  result;
        });
        return $.when(def1);
    },

    render_dashboards: function() {
        var self = this;
        if (this.link_ids){
            _.each(this.dashboards_templates, function(template) {
                self.$('.o_ohada_dashboard').append(QWeb.render(template, {widget: self}));
            });
            }
        else{
            self.$('.o_ohada_dashboard').append(QWeb.render('OhadaWarning', {widget: self}));
            }
    },

    render_graphs: function(){
        var self = this;
        if (this.link_ids){
            self.render_leave_graph();
            self.render_leave_graph2();
            self.update_join_resign_trends();
        }
    },

    get_link: function() {
        var self = this;
        var def1 =  this._rpc({
                model: 'ohada.financial.html.report',
                method: 'get_link',
        }).done(function(result) {
            console.log(result)
        });
        return $.when(def1);
    },


    update_join_resign_trends: function(){
        var elem = this.$('.join_resign_trend');
        var colors = ['#7C7BAD'];
        var color = d3.scale.ordinal().range(colors);
        rpc.query({
            model: 'account.account',
            method: 'search_read',
            fields: ['code'],
        }).then(function (data) {
            var data = [{'name': "Join", 'values':[{count: 1, l_month: "N3"},{count: 5, l_month: "N2"},{count: 4, l_month: "N1"},{count: 6, l_month: "N"}]}]
            data.forEach(function(d) {
              d.values.forEach(function(d) {
                d.l_month = d.l_month;
                d.count = +d.count;
              });
            });
            var margin = {top: 30, right: 0, bottom: 30, left: 0},
                width = 235 - margin.left - margin.right,
                height = 100 - margin.top - margin.bottom;

            // Set the ranges
            var x = d3.scale.ordinal()
                .rangeRoundBands([0, width], 1);

            var y = d3.scale.linear()
                .range([height, 0]);

            // Define the axes
            var xAxis = d3.svg.axis().scale(x)
                .orient("bottom");

            var yAxis = d3.svg.axis().scale(y)
                .orient("left").ticks(5);

            x.domain(data[0].values.map(function(d) { return d.l_month; }));
            y.domain([0, d3.max(data[0].values, d => d.count)])

            var svg = d3.select(elem[0]).append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            // Add the X Axis
            svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

            var line = d3.svg.line()
                .x(function(d) {return x(d.l_month); })
                .y(function(d) {return y(d.count); });

            let lines = svg.append('g')
              .attr('class', 'lines');

            lines.selectAll('.line-group')
                .data(data).enter()
                .append('g')
                .attr('class', 'line-group')
                .append('path')
                .attr('class', 'line')
                .attr('d', function(d) { return line(d.values); })
                .style('stroke', (d, i) => color(i));

            lines.selectAll("circle-group")
                .data(data).enter()
                .append("g")
                .selectAll("circle")
                .data(function(d) { return d.values;}).enter()
                .append("g")
                .attr("class", "circle")
                .append("circle")
                .attr("cx", function(d) { return x(d.l_month)})
                .attr("cy", function(d) { return y(d.count)})
                .attr("r", 3);
        });
    },


    render_leave_graph2:function(){
        var self = this;
        var colors = ['#7C7BAD'];
        var color = d3.scale.ordinal().range(colors);
        rpc.query({
                model: 'account.account',
                method: 'search_read',
                fields: ['code'],
            }).then(function (data) {
//                var fData = data[0];
//                var dept = data[1];
                var fData = [{'l_month': "May 2019", 'leave': {Administration: 0, Management: 0, Sales: 0}},{'l_month': "May 2019", 'leave': {Administration: 0, Management: 0, Sales: 0}},{'l_month': "May 2019", 'leave': {Administration: 0, Management: 0, Sales: 0}}];
                var dept = ["Administration", "Sales", "Management"];
                var id = self.$('.leave_graph2')[0];
                var barColor = '#7C7BAD';
                // compute total for each state.
                fData.forEach(function(d){
                    var total = 0;
                    for (var dpt in dept){
                        total += d.leave[dept[dpt]];
                    }
                d.total=total;
                });

                // function to handle histogram.
                function histoGram(fD){
                    var hG={},    hGDim = {t: 60, r: 0, b: 30, l: 0};
                    hGDim.w = 200 - hGDim.l - hGDim.r,
                    hGDim.h = 100 - hGDim.t - hGDim.b;

                    //create svg for histogram.
                    var hGsvg = d3.select(id).append("svg")
                        .attr("width", hGDim.w + hGDim.l + hGDim.r)
                        .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
                        .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

                    // create function for x-axis mapping.
                    var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
                            .domain(fD.map(function(d) { return d[0]; }));

                    // Add x-axis to the histogram svg.
                    hGsvg.append("g").attr("class", "x axis")
                        .attr("transform", "translate(0," + hGDim.h + ")")
                        .call(d3.svg.axis().scale(x).orient("bottom"));

                    // Create function for y-axis map.
                    var y = d3.scale.linear().range([hGDim.h, 0])
                            .domain([0, d3.max(fD, function(d) { return d[1]; })]);

                    // Create bars for histogram to contain rectangles and freq labels.
                    var bars = hGsvg.selectAll(".bar").data(fD).enter()
                            .append("g").attr("class", "bar");

                    //create the rectangles.
                    bars.append("rect")
                        .attr("x", function(d) { return x(d[0]); })
                        .attr("y", function(d) { return y(d[1]); })
                        .attr("width", x.rangeBand())
                        .attr("height", function(d) { return hGDim.h - y(d[1]); })
                        .attr('fill',barColor);
//                        .on("mouseover",mouseover)// mouseover is defined below.
//                        .on("mouseout",mouseout);// mouseout is defined below.

                    //Create the frequency labels above the rectangles.
                    bars.append("text").text(function(d){ return d3.format(",")(d[1])})
                        .attr("x", function(d) { return x(d[0])+x.rangeBand()/2; })
                        .attr("y", function(d) { return y(d[1])-5; })
                        .attr("text-anchor", "middle");

                    function mouseover(d){  // utility function to be called on mouseover.
                        // filter for selected state.
                        var st = fData.filter(function(s){ return s.l_month == d[0];})[0],
                            nD = d3.keys(st.leave).map(function(s){ return {type:s, leave:st.leave[s]};});

                        // call update functions of pie-chart and legend.
                    }

                    // create function to update the bars. This will be used by pie-chart.
                    hG.update = function(nD, color){
                        // update the domain of the y-axis map to reflect change in frequencies.
                        y.domain([0, d3.max(nD, function(d) { return d[1]; })]);

                        // Attach the new data to the bars.
                        var bars = hGsvg.selectAll(".bar").data(nD);

                        // transition the height and color of rectangles.
                        bars.select("rect").transition().duration(500)
                            .attr("y", function(d) {return y(d[1]); })
                            .attr("height", function(d) { return hGDim.h - y(d[1]); })
                            .attr("fill", color);

                        // transition the frequency labels location and change value.
                        bars.select("text").transition().duration(500)
                            .text(function(d){ return d3.format(",")(d[1])})
                            .attr("y", function(d) {return y(d[1])-5; });
                    }
                    return hG;
                }

                // calculate total frequency by segment for all state.
                var tF = dept.map(function(d){
                    return {type:d, leave: d3.sum(fData.map(function(t){ return t.leave[d];}))};
                });

                // calculate total frequency by state for all segment.
//                var sF = fData.map(function(d){return [d.l_month,d.total];});
                var sF = [['N3',1], ['N2',6], ['N1',3], ['N',2]];
                var hG = histoGram(sF); // create the histogram.
        });
    },

    render_leave_graph:function(){
        var self = this;
//        var color = d3.scale.category10();
        var colors = ['#7C7BAD'];
        var color = d3.scale.ordinal().range(colors);
        rpc.query({
                model: 'account.account',
                method: 'search_read',
                fields: ['code'],
            }).then(function (data) {
//                var fData = data[0];
//                var dept = data[1];
                var fData = [{'l_month': "May 2019", 'leave': {Administration: 0, Management: 0, Sales: 0}},{'l_month': "May 2019", 'leave': {Administration: 0, Management: 0, Sales: 0}},{'l_month': "May 2019", 'leave': {Administration: 0, Management: 0, Sales: 0}}];
                var dept = ["Administration", "Sales", "Management"];
                var id = self.$('.leave_graph')[0];
                var barColor = '#7C7BAD';
                // compute total for each state.
                fData.forEach(function(d){
                    var total = 0;
                    for (var dpt in dept){
                        total += d.leave[dept[dpt]];
                    }
                d.total=total;
                });

                // function to handle histogram.
                function histoGram(fD){
                    var hG={},    hGDim = {t: 60, r: 0, b: 30, l: 0};
                    hGDim.w = 200 - hGDim.l - hGDim.r,
                    hGDim.h = 100 - hGDim.t - hGDim.b;

                    //create svg for histogram.
                    var hGsvg = d3.select(id).append("svg")
                        .attr("width", hGDim.w + hGDim.l + hGDim.r)
                        .attr("height", hGDim.h + hGDim.t + hGDim.b).append("g")
                        .attr("transform", "translate(" + hGDim.l + "," + hGDim.t + ")");

                    // create function for x-axis mapping.
                    var x = d3.scale.ordinal().rangeRoundBands([0, hGDim.w], 0.1)
                            .domain(fD.map(function(d) { return d[0]; }));

                    // Add x-axis to the histogram svg.
                    hGsvg.append("g").attr("class", "x axis")
                        .attr("transform", "translate(0," + hGDim.h + ")")
                        .call(d3.svg.axis().scale(x).orient("bottom"));

                    // Create function for y-axis map.
                    var y = d3.scale.linear().range([hGDim.h, 0])
                            .domain([0, d3.max(fD, function(d) { return d[1]; })]);

                    // Create bars for histogram to contain rectangles and freq labels.
                    var bars = hGsvg.selectAll(".bar").data(fD).enter()
                            .append("g").attr("class", "bar");

                    //create the rectangles.
                    bars.append("rect")
                        .attr("x", function(d) { return x(d[0]); })
                        .attr("y", function(d) { return y(d[1]); })
                        .attr("width", x.rangeBand())
                        .attr("height", function(d) { return hGDim.h - y(d[1]); })
                        .attr('fill',barColor);
//                        .on("mouseover",mouseover)// mouseover is defined below.
//                        .on("mouseout",mouseout);// mouseout is defined below.

                    //Create the frequency labels above the rectangles.
                    bars.append("text").text(function(d){ return d3.format(",")(d[1])})
                        .attr("x", function(d) { return x(d[0])+x.rangeBand()/2; })
                        .attr("y", function(d) { return y(d[1])-5; })
                        .attr("text-anchor", "middle");

                    // create function to update the bars. This will be used by pie-chart.
                    hG.update = function(nD, color){
                        // update the domain of the y-axis map to reflect change in frequencies.
                        y.domain([0, d3.max(nD, function(d) { return d[1]; })]);

                        // Attach the new data to the bars.
                        var bars = hGsvg.selectAll(".bar").data(nD);

                        // transition the height and color of rectangles.
                        bars.select("rect").transition().duration(500)
                            .attr("y", function(d) {return y(d[1]); })
                            .attr("height", function(d) { return hGDim.h - y(d[1]); })
                            .attr("fill", color);

                        // transition the frequency labels location and change value.
                        bars.select("text").transition().duration(500)
                            .text(function(d){ return d3.format(",")(d[1])})
                            .attr("y", function(d) {return y(d[1])-5; });
                    }
                    return hG;
                }

                // calculate total frequency by state for all segment.
//                var sF = fData.map(function(d){return [d.l_month,d.total];});
                var sF = [['N3',5], ['N2',1], ['N1',4], ['N',1]];
                var hG = histoGram(sF); // create the histogram.
        });
    },


});


core.action_registry.add('ohada_dashboard', OhadaDashboard);

return OhadaDashboard;

});