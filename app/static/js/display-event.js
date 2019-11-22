function myFunction(friendlist,id) {
    input = document.getElementById("myInput")
    filter = input.value.toUpperCase();
    var regex=/^[a-zA-Z]+$/;
    document.getElementById("friends").innerHTML = "";
    console.log(friendlist[0]['id'])
    for (i = 0; i < friendlist.length; i++){
        if (friendlist[i]['firstName'].toUpperCase().indexOf(filter) > -1 && filter.match(regex)){
            var node = document.createElement("LI");
            console.log(friendlist[i]['id'])
            var link = "<a href = \"/add-people/" + friendlist[i]['id']+ "/" +id + "\">" + friendlist[i]['firstName'] + " " + friendlist[i]['lastName'] + "</a>"
            console.log(link);
            node.innerHTML = link;
            document.getElementById("friends").appendChild(node);
        }
    }

}
