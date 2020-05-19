$(document).ready(function () {
  var stock_table = $("#stock_table").DataTable({
    aaData: stock,
    columnDefs: [
      {
        targets: -1,
        data: null,
        //defaultContent: "<button><a href='/stock_trade/'>Trade</a></button>",
        render: function (data, type, full, meta) {
          return `<button><a href='/stock_trade/${data[0]}'>Trade</a></button>`;
        }
      },
      {
        targets: [0],
        visible: false,
        searchable: false,
      },
    ],
  });

});
