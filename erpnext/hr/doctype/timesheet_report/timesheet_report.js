cur_frm.cscript.onload = function(doc){
    doc.employee = "";
    doc.from_date = "";
    doc.to_date = "";
    doc.html_code = "";
}

// cur_frm.cscript.employee = function(doc){
//     // console.log(["test","onvalidate"]);
//     cur_frm.call({
//         doc: cur_frm.doc,
//         // method: "get_timesheet_report",
//         method: "get_timesheet_report",
//         callback: function(r) {
//             if(!r.exc) {
//                 // console.log(r.message);
//                 // $("#timesheet").html(r.message);
//                 console.log("test emp")
//             }
//         }
//     });
// }
