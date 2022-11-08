function randomPassword() {
    var length = document.getElementById("passLength").value
    var chars = "abcdefghijklmnopqrstuvwxyz!@#$&*ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890";
    var pass = "";
    for (var x = 0; x < length; x++) {
        var i = Math.floor(Math.random() * chars.length);
        pass += chars.charAt(i);
    }
    nums="1234567890";
    specs="!@#$&*";
    big="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    small="abcdefghijklmnopqrstuvwxyz"
    var noNums=1;
    var noSpecs=1;
    var noSmalls=1;
    var noBigs=1;
    while (true) {
        for (var n = 0; n < nums.length; n++) {
            if (pass.includes(nums.charAt(n))) {
                noNums=0;
            }
        }
        for (var s = 0; s < specs.length; s++) {
            if (pass.includes(specs.charAt(s))) {
                noSpecs=0;
            }
        }
        for (var lw = 0; lw < small.length; lw++) {
            if (pass.includes(small.charAt(lw))) {
                noSmalls=0;
            }
        }
        for (var up = 0; up < big.length; up++) {
            if (pass.includes(big.charAt(up))) {
                noBigs=0;
            }
        }

        if (!noSmalls && !noBigs && !noNums && !noSpecs) {
            break;
        }
        else {
            pass=''
            for (var x = 0; x < length; x++) {
                var i = Math.floor(Math.random() * chars.length);
                pass += chars.charAt(i);
            }
        }
    }
    var el = document.getElementById('passw')
    el.value = pass;
}

function copyToClipboard(x) {
    // Get the text field
    var copyText = document.getElementById(x);

    // Select the text field
    copyText.select();
    copyText.setSelectionRange(0, 99999); // For mobile devices

     // Copy the text inside the text field
    navigator.clipboard.writeText(copyText.value);

    // Alert the copied text
    $("#modal1").modal('show');
}

function passHide(hideId) {
  var x = document.getElementById(hideId);
  var y = document.getElementById("switchVisible");
  if (x.type === "password") {
    x.type = "text";
    y.innerHTML = '<i class="fa fa-eye"></i>';
  }
  else {
    x.type = "password";
    y.innerHTML = '<i class="fa fa-eye-slash"></i>';
  }
}
