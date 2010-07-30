function main() {
    $(".letter").click(open_subdivs);
    $(".letter").css('cursor','pointer');
}

function open_subdivs() {
    $(".subdivs").hide();
    $("#subdivs_"+this.textContent.toLowerCase()).show();
}

$(document).ready(main);

