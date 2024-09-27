function calculate_age(dob) {
    var diff_ms = Date.now() - dob.getTime();
    var age_dt = new Date(diff_ms);

    return Math.abs(age_dt.getUTCFullYear() - 1970);
}

function parseDateOnlyProfile(s) {
    var b = s.split(/\D/);
    return new Date(b[0], --b[1], b[2]);
}


try {



    $(document).ready(function() {
        // debugger;
        var user_only_name = $("#user_only_name");
        var user_last_name = $("#user_last_name");
        if (user_only_name) {
            user_only_name.change(function() {

                let name = user_only_name.val();
                let last_name = user_last_name.val();

                $("#complete_name").val(name);
                // debugger;

            });

        }

        if (user_last_name) {
            user_last_name.change(function() {

                let name = user_only_name.val();
                let last_name = user_last_name.val();

                $("#complete_name").val(name);

            });

        }


        var user_birthday = $("#user_birthday");
        if (user_birthday) {

            let birth_day = user_birthday.val()
            if (birth_day) {
                let birth_date = parseDateOnlyProfile(birth_day);

                let age = calculate_age(birth_date);
                $("#user_age").val(age);
            }

            user_birthday.change(function() {

                let birth_day = user_birthday.val()
                if (birth_day) {
                    let birth_date = parseDateOnlyProfile(birth_day);

                    let age = calculate_age(birth_date);
                    $("#user_age").val(age);
                }



            });


        }

        var state_profile = $("#state_profile");
        var city_profile = $("#city_profile");
        var town_profile = $("#town_profile");
        var sector_profile = $("#sector_profile");


        if (state_profile) {
            var load_state = function() {

                let saved_value = state_profile.val();
                let url_provicias = "https://apip.deparenpar.edu.do/v1/localidad/provincias";
                $.ajax({
                    type: 'GET',
                    url: url_provicias,
                    dataType: 'json',
                    success: function(data_result) {

                        var $el = state_profile;
                        $el.empty(); // remove old options
                        $.each(data_result.data, function(key, value) {

                            if (saved_value && value.id == saved_value) {
                                $el.append($("<option selected></option>")
                                    .attr("value", value.id).text(value.nombre));

                            } else {
                                $el.append($("<option></option>")
                                    .attr("value", value.id).text(value.nombre));
                            }



                        });
                    }

                });
            }

            load_state();
        }


        if (city_profile) {
            var load_city = function() {


                let id_provincia = state_profile.val();
                let saved_value = city_profile.val();
                let url_municipios = `https://apip.deparenpar.edu.do/v1/localidad/provincias/${id_provincia}/municipios`;
                $.ajax({
                    type: 'GET',
                    url: url_municipios,
                    dataType: 'json',
                    success: function(data_result) {

                        var $el = city_profile;
                        $el.empty(); // remove old options
                        $.each(data_result.data, function(key, value) {

                            if (saved_value && value.id == saved_value) {
                                $el.append($("<option selected></option>")
                                    .attr("value", value.id).text(value.nombre));

                            } else {
                                $el.append($("<option></option>")
                                    .attr("value", value.id).text(value.nombre));
                            }



                        });
                    }

                });
            }

            load_city();
        }

        if (town_profile) {
            var load_town = function() {


                let municipio_id = city_profile.val()
                let saved_value = town_profile.val();
                let url_distritos_municipales = `https://apip.deparenpar.edu.do/v1/localidad/municipios/${municipio_id}/distritos_municipales`;
                $.ajax({
                    type: 'GET',
                    url: url_distritos_municipales,
                    dataType: 'json',
                    success: function(data_result) {

                        var $el = town_profile;
                        $el.empty(); // remove old options
                        $.each(data_result.data, function(key, value) {

                            if (saved_value && value.id == saved_value) {
                                $el.append($("<option selected></option>")
                                    .attr("value", value.id).text(value.nombre));

                            } else {
                                $el.append($("<option></option>")
                                    .attr("value", value.id).text(value.nombre));
                            }



                        });
                    }

                });
            }

            load_town();
        }


        if (sector_profile) {
            var load_sector = function() {


                let saved_value = sector_profile.val();
                let distritom_id = town_profile.val();


                let url_sector = `https://apip.deparenpar.edu.do/v1/localidad/distritos_municipales/${distritom_id}/barrios`;

                $.ajax({
                    type: 'GET',
                    url: url_sector,
                    dataType: 'json',
                    success: function(data_result) {

                        var $el = sector_profile;
                        $el.empty(); // remove old options
                        $.each(data_result.data, function(key, value) {

                            if (saved_value && value.id == saved_value) {
                                $el.append($("<option selected></option>")
                                    .attr("value", value.id).text(value.nombre));

                            } else {
                                $el.append($("<option></option>")
                                    .attr("value", value.id).text(value.nombre));
                            }



                        });
                    }

                });
            }

            load_sector();
        }



        var change_info_state = function() {

            let state = state_profile.val()

            if (state) {

                let id_provincia = state

                let url_municipios = `https://apip.deparenpar.edu.do/v1/localidad/provincias/${id_provincia}/municipios`;

                $.ajax({
                    type: 'GET',
                    url: url_municipios,
                    dataType: 'json',
                    success: function(data_result) {
                        console.log(data_result);


                        var $el = city_profile;
                        $el.empty(); // remove old options
                        $.each(data_result.data, function(key, value) {
                            $el.append($("<option></option>")
                                .attr("value", value.id).text(value.nombre));
                        });



                        let municipio_id = city_profile.val()


                        let url_distritos_municipales = `https://apip.deparenpar.edu.do/v1/localidad/municipios/${municipio_id}/distritos_municipales`;

                        $.ajax({
                            type: 'GET',
                            url: url_distritos_municipales,
                            dataType: 'json',
                            success: function(data_result) {
                                console.log(data_result);


                                var $el = town_profile;
                                $el.empty(); // remove old options
                                $.each(data_result.data, function(key, value) {
                                    $el.append($("<option></option>")
                                        .attr("value", value.id).text(value.nombre));
                                });


                                let distritom_id = town_profile.val()


                                let url_sector = `https://apip.deparenpar.edu.do/v1/localidad/distritos_municipales/${distritom_id}/barrios`;

                                $.ajax({
                                    type: 'GET',
                                    url: url_sector,
                                    dataType: 'json',
                                    success: function(data_result) {
                                        console.log(data_result);


                                        var $el = sector_profile;
                                        $el.empty(); // remove old options
                                        $.each(data_result.data, function(key, value) {
                                            $el.append($("<option></option>")
                                                .attr("value", value.id).text(value.nombre));
                                        });



                                    }

                                });


                            }

                        });

                    }
                });



            }



        }

        var change_info_city = function() {


            let municipio_id = city_profile.val()


            let url_distritos_municipales = `https://apip.deparenpar.edu.do/v1/localidad/municipios/${municipio_id}/distritos_municipales`;

            $.ajax({
                type: 'GET',
                url: url_distritos_municipales,
                dataType: 'json',
                success: function(data_result) {
                    console.log(data_result);


                    var $el = town_profile;
                    $el.empty(); // remove old options
                    $.each(data_result.data, function(key, value) {
                        $el.append($("<option></option>")
                            .attr("value", value.id).text(value.nombre));
                    });


                    let distritom_id = town_profile.val()


                    let url_sector = `https://apip.deparenpar.edu.do/v1/localidad/distritos_municipales/${distritom_id}/barrios`;

                    $.ajax({
                        type: 'GET',
                        url: url_sector,
                        dataType: 'json',
                        success: function(data_result) {
                            console.log(data_result);


                            var $el = sector_profile;
                            $el.empty(); // remove old options
                            $.each(data_result.data, function(key, value) {
                                $el.append($("<option></option>")
                                    .attr("value", value.id).text(value.nombre));
                            });






                        }

                    });

                }
            });







        }

        var change_info_town = function() {





            let distritom_id = town_profile.val()


            let url_sector = `https://apip.deparenpar.edu.do/v1/localidad/distritos_municipales/${distritom_id}/barrios`;

            $.ajax({
                type: 'GET',
                url: url_sector,
                dataType: 'json',
                success: function(data_result) {
                    console.log(data_result);


                    var $el = sector_profile;
                    $el.empty(); // remove old options
                    $.each(data_result.data, function(key, value) {
                        $el.append($("<option></option>")
                            .attr("value", value.id).text(value.nombre));
                    });

                }
            });



        }





        if (state_profile) {
            state_profile.change(change_info_state);
        }

        if (city_profile) {
            city_profile.change(change_info_city);
        }

        if (town_profile) {
            town_profile.change(change_info_town);
        }






    });

} catch (error) {
    console.log(error);

}