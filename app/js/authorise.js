function loadUrl(location) {
    console.log(location);
    window.location = location;
}

function authorise(){
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        console.log(this.status + " " + this.response + " " + ajax.readyState)
        if (ajax.readyState==4 && ajax.status==200) {
            var link = "http://" + window.document.location.host + "/charge/" + this.responseText
            console.log(link)
            loadUrl(link);
        }
        if (ajax.readyState== 4 && ajax.status!=200){
            location.reload()
        }
    }
    ajax.open("OPTIONS", "");
    ajax.send();
}

function showAgb(){
    modal.setContent("Wird geladen..")
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        if (ajax.readyState==4 && ajax.status==200) {
            modal.setContent('<h1>Allgemeine Geschäftsbedingungen</h1> '+ this.responseText)
        }
    }
    ajax.open("GET", "/getAgb/");
    ajax.send();
    modal.open()
}

function showPP() {
    modal.setContent("Wird geladen..")
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        if (ajax.readyState==4 && ajax.status==200) {
            modal.setContent('<h1>Privacy Policy</h1> '+ this.responseText)
        }
    }
    ajax.open("GET", "/getPP/");
    ajax.send();
    modal.open()
}
authorise()

var modal = new tingle.modal({
    footer: false,
    stickyFooter: false,
    closeMethods: ['overlay', 'button', 'escape'],
    closeLabel: "Close",
});