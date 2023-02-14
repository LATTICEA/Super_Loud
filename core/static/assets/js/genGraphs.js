var a = new XMLHttpRequest();
a.open("GET","/run-subscription-payment-routine");
a.send();

"use strict";
const d = document;
d.addEventListener("DOMContentLoaded", function(event) {

    // GRAPH
    if ( window.history.replaceState ) {
        window.history.replaceState( null, null, window.location.href );
    }
    function gengraphApex(a){
        if (a){
            area_fil = document.getElementById('area-filter').value;
            industry_fil = document.getElementById('industry-filter').value;
            occupation_fil = document.getElementById('occupation-filter').value;
            skill_fil = document.getElementById('skills-filter').value;

            document.getElementById("chart13").innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>';
            document.getElementById("chart14").innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>';

            fetch('/get-graph-values/' + area_fil + '/' + industry_fil + '/' + occupation_fil + '/' + skill_fil)
            .then((response) => response.json())
            .then((data) => {

                // console.log(data)

                document.getElementById("chart13").innerHTML = '<div class="d-flex justify-content-center"></div>';
                const mainHourlyData = {
                    dates: data.xaxis,
                    series: data.yaxis_hourly.map((d, i) => ({
                        id: d.id
                        , name: d.name
                        , values: d.data
                        , inferred: data.inferred[i]
                    })),
                };
                // console.log("main hourly data:", mainHourlyData);
                const hourly_graph = new WageGraph({
                    el: document.getElementById("chart13")
                    , data: mainHourlyData
                    , type: "hourly"
                });

                document.getElementById("chart14").innerHTML = '<div class="d-flex justify-content-center"></div>';
                const mainAnnuallyData = {
                    dates: data.xaxis,
                    series: data.yaxis_annually.map((d, i) => ({
                        id: d.id
                        , name: d.name
                        , values: d.data
                        , inferred: data.inferred[i]
                    })),
                };

                // console.log("main annually data:", mainAnnuallyData);
                const salary_graph = new WageGraph({
                    el: document.getElementById("chart14"),
                    data: mainAnnuallyData,
                    type: "annually",
                });

                for (let i in data.yaxis_cross_ref) {

                    if (data.labor_force.length > 0) {
                        unemployment_hourly_id = "#unemployment_hourly_cards_".concat("", String(data.yaxis_cross_ref[i].id));
                        unemployment_salary_id = "#unemployment_salary_cards_".concat("", String(data.yaxis_cross_ref[i].id));

                        if (data.yaxis_hourly[i]['data'].length == 40) {
                            inferred_emp = Array(40).fill(0);
                        } else {
                            inferred_emp = Array(48).fill(0);
                        }

                        // Wage and unemployment
                        const wageUnemploymentHourlyData = {
                            dates: data.xaxis
                            , wageSeries: {
                                id: data.yaxis_hourly[i]['id']
                                , name: data.yaxis_hourly[i]['name']
                                , values: data.yaxis_hourly[i]['data']
                                , inferred: data.inferred[i]
                            }
                            , unemploymentSeries: {
                                id: String(data.yaxis_hourly[i]['id'] + '-1')
                                , name: "Unemployment Rate"
                                , values: data.unemployment_rate[i]
                                , inferred: inferred_emp,
                            }
                            , unemploymentCountSeries: {
                                id: String(data.yaxis_hourly[i]['id'] + '-2')
                                , name: "Unemployment"
                                , values: data.unemployment[i]
                                , inferred: inferred_emp,
                            }
                            , employmentSeries: {
                                id: String(data.yaxis_hourly[i]['id'] + '-3')
                                , name: "Employment"
                                , values: data.employment[i]
                                , inferred: inferred_emp,
                            }
                            , laborForceSeries: {
                                id: String(data.yaxis_hourly[i]['id'] + '-4')
                                , name: "Labor Force"
                                , values: data.labor_force[i]
                                , inferred: inferred_emp,
                            },
                        };
                        const hourly_wageUnemploymentGraph = new WageUnemploymentGraph({
                            el: document.querySelector(unemployment_hourly_id),
                            data: wageUnemploymentHourlyData,
                            type: "hourly",
                        });

                        const wageUnemploymentSalaryData = {
                            dates: data.xaxis
                            , wageSeries: {
                                id: data.yaxis_annually[i]['id']
                                , name: data.yaxis_annually[i]['name']
                                , values: data.yaxis_annually[i]['data']
                                , inferred: data.inferred[i]
                            }
                            , unemploymentSeries: {
                                id: String(data.yaxis_annually[i]['id'] + '-1')
                                , name: "Unemployment Rate"
                                , values: data.unemployment_rate[i]
                                , inferred: inferred_emp,
                            }
                            , unemploymentCountSeries: {
                                id: String(data.yaxis_annually[i]['id'] + '-2')
                                , name: "Unemployment"
                                , values: data.unemployment[i]
                                , inferred: inferred_emp,
                            }
                            , employmentSeries: {
                                id: String(data.yaxis_annually[i]['id'] + '-3')
                                , name: "Employment"
                                , values: data.employment[i]
                                , inferred: inferred_emp,
                            }
                            , laborForceSeries: {
                                id: String(data.yaxis_annually[i]['id'] + '-4')
                                , name: "Labor Force"
                                , values: data.labor_force[i]
                                , inferred: inferred_emp,
                            },
                        };
                        const salary_wageUnemploymentGraph = new WageUnemploymentGraph({
                            el: document.querySelector(unemployment_salary_id),
                            data: wageUnemploymentSalaryData,
                            type: "annually",
                        });
                    } else {
                        
                    }

                    if (JSON.parse(JSON.stringify(data.yaxis_cross_ref[i].data)).length >= 1 && JSON.parse(JSON.stringify(data.yaxis_cross_ref[i].data))[0] != null) {
                        chart_hourly_id = "#chart_hourly_cards_".concat("", String(data.yaxis_cross_ref[i].id));
                        chart_salary_id = "#chart_salary_cards_".concat("", String(data.yaxis_cross_ref[i].id));

                        var base_dataset = JSON.parse(JSON.stringify(data.yaxis_hourly[i])).data

                        var options_hourly_series = []
                        var options_salary_series = []

                        // console.log(data.yaxis_hourly[i])
                        // console.log(data.yaxis_annually[i])

                        if (base_dataset.length > 40 && base_dataset[47] === null) {
                            // naics cross-ref
                            options_hourly_series.push({
                                'id': data.yaxis_hourly[i]['id']
                                , 'name': data.yaxis_hourly[i]['name']
                                , 'data': data.yaxis_hourly[i]['data'].slice(0, 40)
                                , 'inferred': data.inferred[i]
                            }); //original data
                            options_salary_series.push({
                                'id': data.yaxis_annually[i]['id']
                                , 'name': data.yaxis_annually[i]['name']
                                , 'data': data.yaxis_annually[i]['data'].slice(0, 40)
                                , 'inferred': data.inferred[i]
                            }); //original data
                        } else {
                            // naics cross-ref
                            options_hourly_series.push({
                                'id': data.yaxis_hourly[i]['id']
                                , 'name': data.yaxis_hourly[i]['name']
                                , 'data': data.yaxis_hourly[i]['data']
                                , 'inferred': data.inferred[i]
                            }); //original data
                            options_salary_series.push({
                                'id': data.yaxis_annually[i]['id']
                                , 'name': data.yaxis_annually[i]['name']
                                , 'data': data.yaxis_annually[i]['data']
                                , 'inferred': data.inferred[i]
                            }); //original data
                        }


                        // console.log(JSON.parse(JSON.stringify(yaxis_cross_ref[i].data)));

                        for (let h in JSON.parse(JSON.stringify(data.yaxis_cross_ref[i].data))) {
                            // console.log(yaxis_cross_ref[i].data[h]);
                            // console.log(yaxis_cross_ref[i].data[h].data_inferred);

                            options_hourly_values = []
                            options_salary_values = []

                            for (let j in data.yaxis_cross_ref[i].data[h].data_hourly) {
                                options_hourly_values.push(data.yaxis_cross_ref[i].data[h].data_hourly[j])
                                options_salary_values.push(data.yaxis_cross_ref[i].data[h].data_annually[j])
                            }

                            // console.log(yaxis_cross_ref[i].data[h]);


                            if (base_dataset.length > 40 && base_dataset[47] === null) {
                                options_hourly_series.push({
                                    "id": data.yaxis_cross_ref[i].data[h].industry_id_cross
                                    , "name": data.yaxis_cross_ref[i].data[h].cross_ref_code_desc
                                    , "data": options_hourly_values.slice(0, 40).reverse()
                                    , "inferred": data.yaxis_cross_ref[i].data[h].data_inferred.reverse()
                                });

                                options_salary_series.push({
                                    "id": data.yaxis_cross_ref[i].data[h].industry_id_cross
                                    , "name": data.yaxis_cross_ref[i].data[h].cross_ref_code_desc
                                    , "data": options_salary_values.slice(0, 40).reverse()
                                    , "inferred": data.yaxis_cross_ref[i].data[h].data_inferred.reverse()
                                });
                            } else if (base_dataset.length === 40) {
                                options_hourly_series.push({
                                    "id": data.yaxis_cross_ref[i].data[h].industry_id_cross
                                    , "name": data.yaxis_cross_ref[i].data[h].cross_ref_code_desc
                                    , "data": options_hourly_values.slice(0, 40).reverse()
                                    , "inferred": data.yaxis_cross_ref[i].data[h].data_inferred.reverse()
                                });

                                options_salary_series.push({
                                    "id": data.yaxis_cross_ref[i].data[h].industry_id_cross
                                    , "name": data.yaxis_cross_ref[i].data[h].cross_ref_code_desc
                                    , "data": options_salary_values.slice(0, 40).reverse()
                                    , "inferred": data.yaxis_cross_ref[i].data[h].data_inferred.reverse()
                                });
                            } else {
                                options_hourly_values = options_hourly_values.reverse()
                                options_salary_values = options_salary_values.reverse()

                                options_hourly_values.push(null, null, null, null, null, null, null, null)
                                options_salary_values.push(null, null, null, null, null, null, null, null)

                                options_hourly_series.push({
                                    "id": data.yaxis_cross_ref[i].data[h].industry_id_cross
                                    , "name": data.yaxis_cross_ref[i].data[h].cross_ref_code_desc
                                    , "data": options_hourly_values
                                    , 'inferred': data.yaxis_cross_ref[i].data[h].data_inferred.reverse()
                                });

                                options_salary_series.push({
                                    "id": data.yaxis_cross_ref[i].data[h].industry_id_cross
                                    , "name": data.yaxis_cross_ref[i].data[h].cross_ref_code_desc
                                    , "data": options_salary_values
                                    , 'inferred': data.yaxis_cross_ref[i].data[h].data_inferred.reverse()
                                });
                            }
                        }

                        // console.log(options_hourly_series);
                        // console.log(options_salary_series);

                        // Cross ref hourly
                          const crossRefHourlyData = {
                            dates: data.xaxis,
                            series: options_hourly_series.map((d) => ({
                              id: d.id,
                              name: d.name,
                              values: d.data,
                              inferred: d.inferred,
                            })),
                          };

                          // Cross ref annually
                          const crossRefAnnuallyData = {
                            dates: data.xaxis,
                            series: options_salary_series.map((d) => ({
                              id: d.id,
                              name: d.name,
                              values: d.data,
                              inferred: d.inferred,
                            })),
                          };


                        // console.log("cross ref hourly data:", crossRefHourlyData);
                        const hourly_crossRef_graph = new WageGraph({
                            el: document.querySelector(chart_hourly_id),
                            data: crossRefHourlyData,
                            type: "hourly",
                        });

                        // console.log("cross ref annually data:", crossRefAnnuallyData);
                        const salary_crossRef_graph = new WageGraph({
                            el: document.querySelector(chart_salary_id),
                            data: crossRefAnnuallyData,
                            type: "annually",
                        });


                    } //end cross-ref IF statement

                    if (data.bands[i].length > 0) {
                        chart_hourly_bands_id = "#chart_hourly_bands_".concat("", String(data.yaxis_cross_ref[i].id));
                        chart_salary_bands_id = "#chart_salary_bands_".concat("", String(data.yaxis_cross_ref[i].id));

                        // console.log("chart_hourly_bands_id:", chart_hourly_bands_id);
                        // console.log("chart_hourly_bands_id:", chart_salary_bands_id);
                        // console.log(data.bands[i][0].hourly.series.map((d) => ({
                        //         id: d.id
                        //         , name: d.name
                        //         , values: d.values
                        //         , inferred: d.inferred
                        //     })));

                        // bands hourly
                        const bandsHourlyData = {
                            dates: data.bands[i][0].hourly.dates
                            , series: data.bands[i][0].hourly.series.map((d) => ({
                                id: d.id
                                , name: d.name
                                , values: d.values
                                , inferred: d.inferred
                            })),
                        };

                        // bands salary
                        const bandsAnnuallyData = {
                            dates: data.bands[i][0].salary.dates
                            , series: data.bands[i][0].salary.series.map((d) => ({
                                id: d.id
                                , name: d.name
                                , values: d.values
                                , inferred: d.inferred
                            })),
                        };

                        // console.log("band hourly data:", bandsHourlyData);
                        const hourly_crossRef_graph = new WageGraph({
                            el: document.querySelector(chart_hourly_bands_id),
                            data: bandsHourlyData,
                            type: "hourly",
                        });

                        // console.log("band salary data:", bandsAnnuallyData);
                        const salary_crossRef_graph = new WageGraph({
                            el: document.querySelector(chart_salary_bands_id),
                            data: bandsAnnuallyData,
                            type: "annually",
                        });

                    } else {

                    }

                } //end for loop for all cards

            });
        }
    } // Close out the genGraph function
    $(document).ready(function (){
        gengraphApex(true);
    });
});


function graphDisco(edit=false) {
    // console.log("function initiated")
    if (edit == true) {
        area_fil = document.getElementById('area-id').value
        industry_fil = document.getElementById('industry-id').value
        // msa_county = document.getElementById('county_msa_switch_value').value
        msa_county = "msa"
    } else {
        area_fil = document.getElementById('sel2').value.split('--==--')[0];
        industry_fil = document.getElementById('sel3').value.split('--==--')[0];
        // msa_county = document.getElementById('county_msa_switch_value').value
        msa_county = "msa"
    }
    // console.log(area_fil, industry_fil)

    document.getElementById("graphDiscoHourly").innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>';
    document.getElementById("graphDiscoSalary").innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>';

    fetch('/graph-disco/' + area_fil + '/' + industry_fil + '/' + msa_county)
    .then((response) => response.json())
    .then((data) => {
        document.getElementById("graphDiscoToggleRow").style.display = "none";

        document.getElementById("graphDiscoHourly").innerHTML = '<div class="d-flex justify-content-center"></div>';
        const mainHourlyData = {
            dates: data.xaxis,
            series: data.yaxis_hourly.map((d, i) => ({
                name: d.name
                , values: d.data
                , inferred: data.inferred[i]
            })),
        };

        // console.log("main hourly data:", mainHourlyData);
        const hourly_graph = new WageGraph({
            el: document.getElementById("graphDiscoHourly")
            , data: mainHourlyData
            , type: "hourly"
        });

        document.getElementById("graphDiscoSalary").innerHTML = '<div class="d-flex justify-content-center"></div>';
        const mainAnnuallyData = {
            dates: data.xaxis,
            series: data.yaxis_annually.map((d, i) => ({
                name: d.name
                , values: d.data
                , inferred: data.inferred[i]
            })),
          };
        // console.log("main annually data:", mainAnnuallyData);
        const salary_graph = new WageGraph({
            el: document.getElementById("graphDiscoSalary"),
            data: mainAnnuallyData,
            type: "annually",
        });


        document.getElementById("graphDiscoToggleRow").style.display = "block";
    });
} // Close out the graphDisco function

function graphDiscoOcc(edit=false) {
    if (edit == true) {
        area_fil = document.getElementById('area-id').value
        industry_fil = document.getElementById('industry-id').value
        occupation_fil = document.getElementById('occupation-id').value
        // msa_county = document.getElementById("county_msa_switch_value").value
        msa_county = 'msa'
    } else {
        area_fil = document.getElementById('sel2').value.split('--==--')[0];
        industry_fil = document.getElementById('sel3').value.split('--==--')[0];
        occupation_fil = document.getElementById('sel4').value.split('--==--')[0];
        // msa_county = document.getElementById("county_msa_switch_value").value
        msa_county = 'msa'
    }
    // console.log(area_fil, industry_fil)

    document.getElementById("graphDiscoHourly").innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>';
    document.getElementById("graphDiscoSalary").innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>';

    // console.log('/graph-disco-occ/' + area_fil + '/' + industry_fil + '/' + msa_county + '/' + occupation_fil);

    fetch('/graph-disco-occ/' + area_fil + '/' + industry_fil + '/' + msa_county + '/' + occupation_fil)
    .then((response) => response.json())
    .then((data) => {
        document.getElementById("graphDiscoToggleRow").style.display = "none";

        document.getElementById("graphDiscoHourly").innerHTML = '<div class="d-flex justify-content-center"></div>';

        const mainHourlyData = {
            dates: data.xaxis,
            series: data.yaxis_hourly.map((d, i) => ({
                name: d.name
                , values: d.data
                , inferred: data.inferred[i]
            })),
          };

        // console.log("main hourly data:", mainHourlyData);
        const hourly_graph = new WageGraph({
            el: document.getElementById("graphDiscoHourly")
            , data: mainHourlyData
            , type: "hourly"
        });

        document.getElementById("graphDiscoSalary").innerHTML = '<div class="d-flex justify-content-center"></div>';
        const mainAnnuallyData = {
            dates: data.xaxis,
            series: data.yaxis_annually.map((d, i) => ({
                name: d.name
                , values: d.data
                , inferred: data.inferred[i]
            })),
          };
        // console.log("main annually data:", mainAnnuallyData);
        const salary_graph = new WageGraph({
            el: document.getElementById("graphDiscoSalary"),
            data: mainAnnuallyData,
            type: "annually",
        });


        document.getElementById("graphDiscoToggleRow").style.display = "block";
    });
} // Close out the graphDiscoOcc function




function graphDiscoCreate(edit=false) {
    // console.log("function initiated")
    if (edit == true) {
        area_fil = document.getElementById('area-id-create').value
        skills_fil = document.getElementById('skills-id-create').value
        skills_fil = skills_fil.split(",");
        // skills_fil = $('#selCreate3').val()
        // msa_county = document.getElementById('county_msa_switch_value').value
        msa_county = "msa"
    } else {
        area_fil = document.getElementById('selCreate2').value.split('--==--')[0]
        skills_fil = $('#selCreate3').val()
        // msa_county = document.getElementById('county_msa_switch_value').value
        msa_county = "msa"
    }
    
    if (skills_fil.length > 0) {
        for (let index = 0; index < skills_fil.length; index++) {
            skills_fil[index] =  "'" + skills_fil[index].trim() + "'";
        }
        document.getElementById("graphDiscoHourlyCreate").innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>';
        document.getElementById("graphDiscoSalaryCreate").innerHTML = '<div class="d-flex justify-content-center"><div class="spinner-border" role="status"></div></div>';

        fetch('/graph-disco-create/' + area_fil + '/' + "[" + skills_fil + "]")
        .then((response) => response.json())
        .then((data) => {
            document.getElementById("graphDiscoToggleRowCreate").style.display = "none";

            document.getElementById("graphDiscoHourlyCreate").innerHTML = '<div class="d-flex justify-content-center"></div>';
            const mainHourlyData = {
                dates: data.xaxis,
                series: data.yaxis_hourly.map((d, i) => ({
                    name: d.name
                    , values: d.data
                    , inferred: data.inferred[i]
                })),
            };

            // console.log("main hourly data:", mainHourlyData);
            const hourly_graph = new WageGraph({
                el: document.getElementById("graphDiscoHourlyCreate")
                , data: mainHourlyData
                , type: "hourly"
            });

            document.getElementById("graphDiscoSalaryCreate").innerHTML = '<div class="d-flex justify-content-center"></div>';
            const mainAnnuallyData = {
                dates: data.xaxis,
                series: data.yaxis_annually.map((d, i) => ({
                    name: d.name
                    , values: d.data
                    , inferred: data.inferred[i]
                })),
              };
            // console.log("main annually data:", mainAnnuallyData);
            const salary_graph = new WageGraph({
                el: document.getElementById("graphDiscoSalaryCreate"),
                data: mainAnnuallyData,
                type: "annually",
            });


            document.getElementById("graphDiscoToggleRowCreate").style.display = "block";
        });
    }
} // Close out the graphDisco function