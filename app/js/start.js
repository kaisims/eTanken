function checkChargeEnd() {
    var ajax = new XMLHttpRequest();
    ajax.onreadystatechange = function () {
        //console.log(this.status + " " + this.response + " " + ajax.readyState)
        if (ajax.readyState === 4 && ajax.status === 200) {
            console.log("Charge End!")
            var link = "http://" + window.document.location.host + "/stopCharge/" + this.response["receipt"] + "?amount=" + this.response["amount"]
            loadUrl(link);
        } else if (ajax.readyState === 4 && ajax.status === 204) {
            console.log("Check again later")
            sleep(10000).then(() => checkChargeEnd())
        }
    }
    ajax.open("OPTIONS", "/stopCharge/");
    ajax.responseType = 'json';
    ajax.send();
}
checkChargeEnd()