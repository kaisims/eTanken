function loadUrl(location) {
    console.log(location);
    window.location = location;
}

function authorise(){
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        //console.log(this.status + " " + this.response + " " + ajax.readyState)
        if (ajax.readyState===4 && ajax.status===200) {
            var link = "http://" + window.document.location.host + "/charge/" + this.responseText
            loadUrl(link);
        }
        else if (ajax.readyState=== 4 && ajax.status===204){
            console.log("again")
            sleep(1000).then(()=>authorise())
        }
        else if (ajax.readyState=== 4){
            link = "http://" + window.document.location.host + "/chooseChargePoint/"
            loadUrl(link);
        }
    }
    ajax.open("OPTIONS", "");
    ajax.send();
}

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

var modal = new tingle.modal({
    footer: false,
    stickyFooter: false,
    closeMethods: ['overlay', 'button', 'escape'],
    closeLabel: "Close",
});

const sleep = (milliseconds) => {
  return new Promise(resolve => setTimeout(resolve, milliseconds))
}

authorise()