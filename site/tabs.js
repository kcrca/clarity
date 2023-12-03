
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    document.getElementById(tabName).style.display = "block";
    activeButtons = document.getElementsByClassName(tabName);
    for (i = 0; i < activeButtons.length; i++) {
        activeButtons[i].className += " active";
    }
}

tab_name = location.hash.substring(1);
if (!tab_name) {
    tab_name = "Overview";
}

document.addEventListener("DOMContentLoaded", function(event) { 
    openTab(null, tab_name);
});
