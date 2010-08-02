function main() {
    $(".dir").click(select_dir);
    $(".letter").click(open_subdivs);
    $(".subdivs td span").click(goto_subdiv);
}

function select_dir() {
    $("#letters").show();
    dir = this.id;
    $(".dir").removeClass("sel");
    $(this).addClass("sel");
    $(".subdivs").hide();
    $("#content").attr("src", "about:blank");
}

function open_subdivs() {
    $(".subdivs").hide();
    $("#subdivs_"+dir+"_"+this.textContent.toLowerCase()).show();
    $("#content").attr("src", "about:blank");
}

function goto_subdiv() {
    var subdiv = this.textContent;
    $("#content").attr("src", dir+"/"+subdiv+".html");
}


dir = null;
$(document).ready(main);



