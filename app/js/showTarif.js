function showAgb(){
    modal.setContent("Wird geladen..")
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        //console.log("AGB " +this.status + " "  + ajax.readyState)
        if (ajax.readyState===4 && ajax.status===200) {
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
        //console.log("PP " +this.status + " " + ajax.readyState)
        if (ajax.readyState===4 && ajax.status===200) {
            modal.setContent('<h1>Privacy Policy</h1> '+ this.responseText)
        }
    }
    ajax.open("GET", "/getPP/");
    ajax.send();
    modal.open()
}

function showTariff(){
    modal.setContent(document.getElementById("extraTariff").innerHTML)
    modal.open()
}

var modal = new tingle.modal({
    footer: false,
    stickyFooter: false,
    closeMethods: ['overlay', 'button', 'escape'],
    closeLabel: "Close",
});