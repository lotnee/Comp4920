function myFunction(friendlist,id,whichModal,whichInput) {
    input = document.getElementById(whichInput)
    filter = input.value.toUpperCase();
    var regex=/^[a-zA-Z]+$/;
    document.getElementById(whichModal).innerHTML = "";
    for (i = 0; i < friendlist.length; i++){
        if (friendlist[i]['firstName'].toUpperCase().indexOf(filter) > -1 && filter.match(regex)){
            var node = document.createElement("LI");
            if (whichModal == "friends"){
                var link = "<a class = \"friends\" href = \"/add-people/" + friendlist[i]['id']+ "/" +id + "\">" + friendlist[i]['firstName'] + " " + friendlist[i]['lastName'] + "</a>"
            } else {
                var link = "<a class = \"friends\" href = \"/add-coHost/" + friendlist[i]['id']+ "/" +id + "\">" + friendlist[i]['firstName'] + " " + friendlist[i]['lastName'] + "</a>"
            }
            node.innerHTML = link;
            document.getElementById(whichModal).appendChild(node);
        }
    }

}
