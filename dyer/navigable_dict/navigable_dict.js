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

function make_link(keyword, articleIds) {
    return "<a href=\"javascript:load_articles('"+articleIds.join(",")+"')\">"+keyword+"</a>";
}

function recursive_enumerate(prefix, trieNode, limit, results) {
    for (var key in trieNode) {
        var value = trieNode[key];
        if (value.constructor == Array) {
            results.push([prefix+key, value]);
        } else {
            recursive_enumerate(prefix+key, value, limit, results);
        }
        if (results.length >= limit) break;
    }
}

function refresh_wordlist() {
    var query = $("#searchbox").val();
    if (query!=oldQuery && query!="") {
        oldQuery = query;
        var trie = searchIndex_all[dir];
        var exact = [];
        var partial = [];
        var trieNode = trie;
        var notExists = false;
        var partialMatches = [];
        console.log(query);
        for (var i=0; i<query.length; i++) {
            var ch = query.charAt(i);
            if (!trieNode.hasOwnProperty(ch)) {
                // no deeper trie char-nodes
                notExists = true;
                // our last chance is that there's an appropriate tail-node
                var tail1 = query.substr(i);
                for (var key in trieNode) {
                    if (key.length>1 && key.substr(0, tail1.length)==tail1) {
                        partialMatches.push([query.substr(0,i)+key, trieNode[key]]);
                        break;
                    }
                }
                break;
            }
            trieNode = trieNode[ch];
            var tail = query.substr(i+1);
            if (trieNode.hasOwnProperty(tail) && trieNode[tail].constructor == Array) {
                exact.push(make_link(query, trieNode[tail]));
            }
        }
        if (!notExists) {
            recursive_enumerate(query, trieNode, 100, partialMatches);
        }
        var res = exact.join("<br>");
        if (exact.length) res += "<hr>";
        if (partialMatches.length>=30) {
            var len = partialMatches.length>=100 ? "100+" : partialMatches.length;
            res += len + " matching words found";
        } else {

            for (var i=0; i<partialMatches.length; i++) {
                var entry = partialMatches[i];
                partial.push(make_link(entry[0], entry[1]));
            }
            res += partial.join("<br>");
        }
        $("#words")[0].innerHTML = res;
    }
    setTimeout(refresh_wordlist, 500);
}

function load_articles(idsByComma) {
    var ids = idsByComma.split(",");
    var loading = false;
    for (var i=0; i<ids.length; i++) {
        var id = ids[i];
        var base = Math.floor(id/100);
        if (!articleChunks[dir].hasOwnProperty(base)) {
            var headID = document.getElementsByTagName("head")[0];
            var script = document.createElement('script');
            baseText = ""+base;
            while (baseText.length<4) {
                baseText = "0"+baseText;
            };
            script.src = dir+"/"+baseText+".js";
            headID.appendChild(script);
            loading = true;
        }
    }
    if (loading) {
        $("#content")[0].innerHTML = "<i>Loading...</i>";
        setTimeout(function(){actually_load_articles(ids)}, 100);
    } else {
        actually_load_articles(ids);
    }
}

function actually_load_articles(ids) {
    var res = [];
    var loading = false;
    for (var i=0; i<ids.length; i++) {
        var id = ids[i];
        var base = Math.floor(id/100);
        var rem = id % 100;
        if (articleChunks[dir].hasOwnProperty(base)) {
            res.push(articleChunks[dir][base][rem]);
        } else {
            loading = true;
        }
    }
    if (loading) {
        res.push("<i>Loading...</i>");
        setTimeout(function(){actually_load_articles(ids)}, 100);
    }
    $("#content")[0].innerHTML = res.join("<hr>");
}


dir = null;
$(document).ready(main);
articleChunks={"en":{}, "io":{}}



