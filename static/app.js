// This project was developed with the assistance of GitHub Copilot and CS50's Duck Debugger (ddb).

document.addEventListener('DOMContentLoaded', function() {
    const addVolumeGroupButton = document.getElementById('addVolumeGroup');
    if (addVolumeGroupButton) { // Ensure the element exists before attaching event listeners
        addVolumeGroupButton.addEventListener('click', addVolumeGroup);
    }
    document.addEventListener('input', updateSubmitButtonState);

    // Initialize the form
    if (document.getElementById('volumeFields')) {
        updateVolumeFields();
    }
        
    // Ensure the total is correct after the initial volume group is added
    if (document.getElementById('volumesTotal')) {
        updateVolumesTotal();
    }

    // Attach the validateAndSubmitForm function to the form's submit event
    const mainForm = document.getElementById('mainForm');
    if (mainForm) {
        mainForm.addEventListener('submit', validateAndSubmitForm);
    }

    // Attach functions to the input fields, if they exist
    const cnpjRemetente = document.getElementById('cnpjRemetente');
    if (cnpjRemetente) {
        cnpjRemetente.addEventListener('input', formatCNPJCPF);
        cnpjRemetente.addEventListener('input', resetCustomValidity);
    }

    const cnpjDestinatario = document.getElementById('cnpjDestinatario');
    if (cnpjDestinatario) {
        cnpjDestinatario.addEventListener('input', formatCNPJCPF);
        cnpjDestinatario.addEventListener('input', resetCustomValidity);
        console.log('reset custom validity worked'); //TEST
    }

    const cepOrigem = document.getElementById('cepOrigem');
    if (cepOrigem) {
        cepOrigem.addEventListener('input', formatCEP);
        cepOrigem.addEventListener('input', resetCustomValidity);
    }

    const cepDestino = document.getElementById('cepDestino');
    if (cepDestino) {
        cepDestino.addEventListener('input', formatCEP);
        cepDestino.addEventListener('input', resetCustomValidity);
    }

    const emailEnvio = document.getElementById('emailEnvio');
    if (emailEnvio) {
        emailEnvio.addEventListener('input', formatEmail);
        emailEnvio.addEventListener('input', resetCustomValidity);
    }
});


let volumeGroupIds = [];
let volumeGroupIdCounter = 1;

function formatCNPJCPF(event) {
    const input = event.target;
    let value = input.value.replace(/\D/g, ''); // Remove all non-digit characters

    if (value.length <= 11) {
        // Format as CPF (XXX.XXX.XXX-XX)
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
    } else if (value.length <= 14) {
        // Format as CNPJ (XX.XXX.XXX/XXXX-XX)
        value = value.replace(/(\d{2})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1.$2');
        value = value.replace(/(\d{3})(\d)/, '$1/$2');
        value = value.replace(/(\d{4})(\d{1,2})$/, '$1-$2');
    }

    input.value = value;
}

function formatCEP(event) {
    const input = event.target;
    let value = input.value.replace(/\D/g, '');

    if (value.length <= 8) {
        // Format as CEP (XX.XXX-XXX)
        value = value.replace(/(\d{2})(\d{3})(\d{3})$/, '$1.$2-$3');
    }

    input.value = value;
}

function formatEmail(event) {
    const input = event.target;
    let value = input.value;

    // Regular expression for validating email format
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    // Check if the email format is valid
    if (!emailPattern.test(value)) {
        input.setCustomValidity('Por favor, insira um e-mail válido.');
    } else {
        input.setCustomValidity('');
    }
}

function updateVolumeFields() {
    const volumeFieldsContainer = document.getElementById('volumeFields');
    if (volumeFieldsContainer) {
        // Clear existing volume fields and reset counter
        volumeFieldsContainer.innerHTML = '';
        volumeGroupIdCounter = 1; // Reset counter for volume groups
        volumeGroupIds = []; // Reset volumeGroupIds array
        addVolumeGroup(); // Add the first volume group
        updateVolumeGroupIds(); // Call updateVolumeGroupIds()
    }
}

// Add a hidden input field for volumeGroupIds if not already present
function updateVolumeGroupIds() {
    document.getElementById('volumeGroupIds').value = volumeGroupIds.join(',');
}

// Adds a volumeGroup to the form, using the volumeGroupIdCounter as the ID
function addVolumeGroup() {
    const volumeFieldsContainer = document.getElementById('volumeFields');
    const volumeGroupHTML = `
        <div class="volume-group" id="volumeGroup${volumeGroupIdCounter}">
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="idAltura${volumeGroupIdCounter}">Altura do volume(m):</label>
                    <input required autocomplete="off" class="form-control format-number" type="number" id="idAltura${volumeGroupIdCounter}" name="altura${volumeGroupIdCounter}" placeholder="Altura do volume" step="0.01">
                </div>
                <div class="col-md-6 mb-3">
                    <label for="idLargura${volumeGroupIdCounter}">Largura do volume(m):</label>
                    <input required autocomplete="off" class="form-control format-number" type="number" id="idLargura${volumeGroupIdCounter}" name="largura${volumeGroupIdCounter}" placeholder="Largura do volume" step="0.01">
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="idComprimento${volumeGroupIdCounter}">Comprimento do volume(m):</label>
                    <input required autocomplete="off" class="form-control format-number" type="number" id="idComprimento${volumeGroupIdCounter}" name="comprimento${volumeGroupIdCounter}" placeholder="Comprimento do volume" step="0.01">
                </div>
                <div class="col-md-6 mb-3">
                    <label for="idVolumes${volumeGroupIdCounter}">Quantidade de volumes:</label>
                    <input required autocomplete="off" class="form-control dynamicVolumes" type="number" id="idVolumes${volumeGroupIdCounter}" name="volumes${volumeGroupIdCounter}" placeholder="Quantidade de volumes" oninput="updateVolumesTotal()">
                </div>
                <div class="col-md-6 mb-3">
                    <button type="button" class="btn btn-danger" onclick="removeVolumeGroup(${volumeGroupIdCounter})">Remover volume</button>
                </div>
            </div>
        </div>
    `;
    volumeFieldsContainer.insertAdjacentHTML('beforeend', volumeGroupHTML);
    // volumeFieldsContainer.innerHTML += volumeGroupHTML;
    volumeGroupIds.push(volumeGroupIdCounter);
    volumeGroupIdCounter += 1; // Increment the counter after adding a new volume group
    updateVolumeGroupIds();
}

function removeVolumeGroup(volumeGroupId) {
    const volumeGroup = document.getElementById(`volumeGroup${volumeGroupId}`);
    if (volumeGroup) {
        // Ensure volumeGroupId is of the same type as the elements in volumeGroupIds
        const isNumericArray = typeof volumeGroupIds[0] === 'number';
        const normalizedVolumeGroupId = isNumericArray ? Number(volumeGroupId) : String(volumeGroupId);

        // Remove volumeGroupId from volumeGroupIds
        const index = volumeGroupIds.indexOf(normalizedVolumeGroupId);
        if (index > -1) {
            volumeGroupIds.splice(index, 1);
        }
        
        volumeGroup.remove();

        updateVolumeGroupIds();

        updateVolumesTotal();
    } else {
        // If the element wasn't found, log or handle the error
        console.error(`Volume group with ID ${volumeGroupId} not found.`);
    }
}

function updateVolumesTotal() {
    let total = 0;

    // Select all the input fields with the class 'dynamicVolumes' and calculate the total
    document.querySelectorAll('.dynamicVolumes').forEach(function(input) {
        total += parseInt(input.value, 10) || 0;
    });

    const volumesTotalElement = document.getElementById('volumesTotal');
    if (volumesTotalElement) {
        volumesTotalElement.value = total;
    }
}

// Format number fields to two decimal places on blur
document.addEventListener('blur', function(event) {
    if (event.target.classList.contains('format-number')) {
        var value = parseFloat(event.target.value);
        if (!isNaN(value)) {
            event.target.value = value.toFixed(2);
        }
    }
}, true);

function showNotification(message) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.style.display = 'block';

    // Hide the notification after 3 seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

function resetCustomValidity(event) {
    event.target.setCustomValidity('');
}

function validateAndSubmitForm(event) {
    let allFilled = true;
    let validCEP = true;
    let validCNPJCPF = true;

    document.querySelectorAll('#mainForm input.form-control').forEach(function(input) {
        if (input.value === '') {
            allFilled = false;
        }
        // Reset custom validity messages
        input.setCustomValidity('');
    });

    // Validate CEP fields
    const cepOrigem = document.getElementById('cepOrigem');
    const cepDestino = document.getElementById('cepDestino');
    const cepPattern = /^\d{2}\.\d{3}-\d{3}$/; // Regular expression for CEP format (XX.XXX-XXX)

    if (cepOrigem && !cepPattern.test(cepOrigem.value)) {
        validCEP = false;
        cepOrigem.setCustomValidity('Por favor, insira um CEP válido.');
    }

    if (cepDestino && !cepPattern.test(cepDestino.value)) {
        validCEP = false;
        cepDestino.setCustomValidity('Por favor, insira um CEP válido.');
    }

    // Validate CNPJ/CPF fields
    const cnpjRemetente = document.getElementById('cnpjRemetente');
    const cnpjDestinatario = document.getElementById('cnpjDestinatario');
    const cnpjCpfPattern = /^(\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}|\d{3}\.\d{3}\.\d{3}-\d{2})$/; // Regular expression for formatted CNPJ or CPF

    if (cnpjRemetente && !cnpjCpfPattern.test(cnpjRemetente.value)) {
        validCNPJCPF = false;
        cnpjRemetente.setCustomValidity('Por favor, insira um CNPJ ou CPF válido.');
    }

    if (cnpjDestinatario && !cnpjCpfPattern.test(cnpjDestinatario.value)) {
        validCNPJCPF = false;
        cnpjDestinatario.setCustomValidity('Por favor, insira um CNPJ ou CPF válido.');
    }

    if (allFilled && validCEP && validCNPJCPF) {
        const volumeGroupIdsInput = document.getElementById('volumeGroupIds');
        if (volumeGroupIdsInput) { // Check if the volumeGroupIds input exists
            volumeGroupIdsInput.value = volumeGroupIds.join(','); // Set the value
        }

        const mainForm = document.getElementById('mainForm');
        if (mainForm) { // Check if the mainForm exists before submitting
            document.getElementById('loading-container').style.display = 'flex'; // Show the loading animation
            mainForm.style.display = 'none'; // Hide the form
            console.log('Form is valid, submitting...'); //TEST
            mainForm.submit(); // This submits the form
        }
    } else {
        event.preventDefault(); // Prevent form submission
        document.querySelectorAll('#mainForm input.form-control').forEach(function(input) {
            input.reportValidity();
        });
        showNotification('Dados errados, favor revisar os campos preenchidos.');
        return false;
    }
}

function updateSubmitButtonState() {
    let allFilled = true;
    document.querySelectorAll('#mainForm input.form-control').forEach(function(input) {
        if (input.value === '') {
            allFilled = false;
        }
    });

    const submitButton = document.getElementById('submitButton');
    if (submitButton) { // Check if the submitButton exists
        submitButton.disabled = !allFilled;
    }
}