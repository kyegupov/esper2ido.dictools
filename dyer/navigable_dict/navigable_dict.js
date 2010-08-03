function main() {
    $(".dir").click(select_dir);
    $("#letters td").click(open_subdivs);
}

function select_dir() {
    $("#letters").show();
    $("#subdivs")[0].innerHTML = "";
    dir = this.id;
    $(".dir").removeClass("sel");
    $(this).addClass("sel");
    $("#content").attr("src", "about:blank");
}

function open_subdivs() {
    var subdivs = subdivs_all[dir+"_"+this.textContent.toLowerCase()];
    var rownum = Math.ceil(subdivs.length/2.0);
    var text = "";
    for (var i=0; i<rownum; i++) {
        text += "<tr>";
        for (var j=0; j<2; j++) {
            var sd = subdivs[j*rownum+i];
            if (sd!==undefined) {
                text += "<td><span>"+sd+"</span></td>";
            } else {
                text += "<td>&nbsp;</td>";
            }
        }
        text += "</tr>";
    }
    $("#subdivs")[0].innerHTML = text;
    $("#subdivs td span").click(goto_subdiv);
    $("#content").attr("src", "about:blank");
}

function goto_subdiv() {
    var subdiv = this.textContent;
    $("#content").attr("src", dir+"/"+subdiv+".html");
}


dir = null;
$(document).ready(main);



