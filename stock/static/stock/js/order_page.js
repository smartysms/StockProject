
$(document).ready(function () {
    console.log(pending_data)
    console.log(history_data)
    var pending_table = $("#pending_table").DataTable({
        aaData: pending_data,
        columnDefs: [
            {
                targets: -2,
                data: null,
                render: function (data, type, full, meta) {
                    return `<button><a href='/modify_order/${data[0]}'>Modify</a></button>`;
                }
            },
            {
                targets: -1,
                data: null,
                render: function (data, type, full, meta) {
                    return `<button><a href='/order_cancel/${data[0]}'>Cancel</a></button>`;
                }
            },
            {
                targets: [0],
                visible: false,
                searchable: false,
            },
        ],
    });


    var history_table = $("#history_table").DataTable({
        aaData: history_data,
    });

    function toggleIcon(e) {
        $(e.target)
            .prev('.panel-heading')
            .find(".more-less")
            .toggleClass('glyphicon-plus glyphicon-minus');
    }
    $('.panel-group').on('hidden.bs.collapse', toggleIcon);
    $('.panel-group').on('shown.bs.collapse', toggleIcon);
});