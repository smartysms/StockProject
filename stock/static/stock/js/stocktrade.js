$(document).ready(function () {

    if (is_applicable_for_sale === 'False') {
        $("select option[value*='sell']").prop('disabled', true);
    }


    $('#id_action').on('change', function () {
        $("input[type=radio]").prop({
            "disabled": false
        })

        let action_type = $(this).val()

        if (action_type == 'buy') {
            $("input[type=radio][value=ask],input[type = radio][value =ipo]").prop({ "disabled": true, "checked": false });
            $("#id_price").prop("value", default_price)

        }
        else if (action_type == 'sell') {
            $("input[type=radio][value=bid],input[type=radio][value=ipo]").prop({ "disabled": true, "checked": false });
            $("#id_price").prop("value", default_price)


        } else {
            $("input[type=radio][value=ipo]").prop({ "disabled": false, "checked": true });
            $("#id_price").prop({ "value": default_price })
            $("input[type=radio][value=ask],input[type=radio][value=market_order],input[type=radio][value=bid]").prop({ "disabled": true, "checked": false });

        }
    });

    $('input[type=radio][name=sale_type]').change(function () {
        if (this.value == 'market_order') {
            $("#id_price").prop("value", default_price)

        }

    });

});
