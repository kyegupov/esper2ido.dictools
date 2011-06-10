function main() {
    $(".dir").click(select_dir);
    $("#searchbox").change(refresh_wordlist);
    select_dir.call($("#en")[0]);
    setTimeout(refresh_wordlist, 500);
    window.oldQuery = "";
}

function select_dir() {
    $("#letters").show();
    dir = this.id;
    $(".dir").removeClass("sel");
    $(this).addClass("sel");
}

function refresh_wordlist() {
    var query = $("#searchbox").val();
    if (query!=oldQuery) {
        oldQuery = query;
        var words = wordlist_all[dir];
        var exact = [];
        var partial = [];
        for (var i=0; i<words.length; i++) {
            if (words[i]==query) {
                exact.push("<a href=\"#\" onclick=\"load_word('"+words[i]+"')\">"+words[i]+"</a>");
            } else if (words[i].indexOf(query)==0) {
                partial.push("<a href=\"#\" onclick=\"load_word('"+words[i]+"')\">"+words[i]+"</a>");
            }
        }
        var res = exact.join("<br>");
        if (exact.length) res += "<hr>";
        if (partial.length>30) {
            res += partial.length + " matching words found";
        } else {
            res += partial.join("<br>");
        }
        $("#words")[0].innerHTML = res;
    }
    setTimeout(refresh_wordlist, 500);
}

function load_word(word) {
    for (var preflen=3; preflen>=1; preflen--) {
        var pref = word.substr(0, preflen);
        while (pref.length<preflen) pref += "_";
        for (var i=0; i<subdivs_all[dir].length; i++) {
            if (subdivs_all[dir][i]==pref) {
                $("#content")[0].src = dir+"/"+pref+".html#"+word;
                return;
            }
        }
    }
}



dir = null;
$(document).ready(main);



