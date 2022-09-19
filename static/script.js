setInterval("checkResult();",3000);
var ajax = typeof XMLHttpRequest == "undefined"?new ActiveXObject('Microsoft.XMLHttp'):new XMLHttpRequest();
function checkResult(){
    var pagePiece=document.getElementById("status");
    ajax.open("GET", "status");
    ajax.send(null);
    ajax.onreadystatechange = function(){
        if(ajax.readyState==4 && ajax.status==200 && ajax.responseText.length!=0){
            response=JSON.parse(ajax.responseText);
            console.log(ajax.responseText);
            pagePiece.innerHTML = response["text"];
            if (response["state"] == "closed")
                pagePiece.style.backgroundColor = "lightgreen";
            else if  (response["state"] == "open")
                pagePiece.style.backgroundColor = "lightpink";
        }
    }

}

document.addEventListener("load",checkResult);
