function check_consistency(id_training) {
    $.ajax({
        url: "/training/check_consistency/",
        type: "GET",
        data: {
            training_id: id_training,
        },
        success: function (data) {
            $("#report-list").empty()
            let empty = true;
            $.each(data.report, function (key, value) {
                empty = false;
                let table = document.createElement("table");
                table.className = "listed";
                let tr_title = document.createElement("tr");
                let title_element = document.createElement("th");
                let title = value.title;
                title_element.innerHTML = title
                tr_title.append(title_element)
                table.append(tr_title)
                $("#report-list").append(table)
                let len = 0;
                $.each(value.objects, function (k, v) {
                    if (len === 0) {
                        len = Object.keys(v).length;
                        title_element.colSpan = len;
                        console.log(len)
                    }
                    let tr = document.createElement("tr");
                    table.append(tr)
                    $.each(v, function (y, z) {
                        td = document.createElement('td');
                        tr.append(td);
                        td.innerHTML = z;
                    })
                });
            });
            if (empty){
                let para = document.createElement('p');
                para.innerHTML = "---";
                $("#report-list").empty();
                $("#report-list").append(para);
            }
            $('#consistency_report').modal('show');
        }
    });
}