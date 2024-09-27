function onlyNumberKey(evt) {
    // Only ASCII charactar in that range allowed
    var ASCIICode = (evt.which) ? evt.which : evt.keyCode
    if (ASCIICode > 31 && (ASCIICode < 48 || ASCIICode > 57))
        return false;
    return true;
}
function alphaOnly(event) {
    var key = event.keyCode;
    return ((key >= 65 && key <= 90) || key == 8);
};

let formatPhoneNumber = (str) => {
    //Filter only numbers from the input
    // debugger;
    let cleaned = ('' + str).replace(/\D/g, '');

    if (cleaned && cleaned.startsWith("1")) {
        cleaned = cleaned.substring(1)
    }
    //Check if the input is of correct length
    let match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/);

    if (match) {
        return '(' + match[1] + ') ' + match[2] + '-' + match[3]
    };

    return null
};

function formatPhone(obj) {
    var numbers = obj.value.replace(/\D/g, ''),
        char = { 0: '(', 3: ') ', 6: '-' };
    obj.value = '';
    for (var i = 0; i < numbers.length; i++) {
        obj.value += (char[i] || '') + numbers[i];
    }
}

try {
    $(document).ready(function() {
        var phone_Format = $("#phoneFormat");
        if (phone_Format) {
            phone_Format.val(formatPhoneNumber(phone_Format.val()))
        }
    });

} catch (error) {
    console.log(error);
}