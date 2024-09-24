document.addEventListener('DOMContentLoaded', function() {
    // Attach event listeners
    document.getElementById('addVolumeGroup').addEventListener('click', addVolumeGroup);
    document.addEventListener('input', updateSubmitButtonState);

    // Initialize the form
    updateVolumeFields();
        
    // Ensure the total is correct after the initial volume group is added
    updateVolumesTotal();

    // Attach the validateAndSubmitForm function to the form's submit event
    document.getElementById('mainForm').addEventListener('submit', validateAndSubmitForm);

    // Attach the formatCNPJCPF function to the CNPJ input fields
    document.getElementById('cnpjRemetente').addEventListener('input', formatCNPJCPF);
    document.getElementById('cnpjDestinatario').addEventListener('input', formatCNPJCPF);

    // Attach the formatCEP function to the CEP input fields
    document.getElementById('cepOrigem').addEventListener('input', formatCEP);
    document.getElementById('cepDestino').addEventListener('input', formatCEP);
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
    let value = input.value.replace(/\D/g, ''); // Remove all non-digit characters

    if (value.length <= 8) {
        // Format as CEP (XXXXX-XXX)
        value = value.replace(/(\d{5})(\d{3})$/, '$1-$2');
    }

    input.value = value;
}

function updateVolumeFields() {
    // Clear existing volume fields and reset counter
    const volumeFieldsContainer = document.getElementById('volumeFields');
    volumeFieldsContainer.innerHTML = '';
    volumeGroupIdCounter = 1; // Reset counter for volume groups
    volumeGroupIds = []; // Reset volumeGroupIds array
    addVolumeGroup(); // Add the first volume group
    updateVolumeGroupIds(); // Call updateVolumeGroupIds()
}

// Add a hidden input field for volumeGroupIds if not already present
function updateVolumeGroupIds() {
    document.getElementById('volumeGroupIds').value = volumeGroupIds.join(',');
}


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
    document.getElementById('volumesTotal').value = total;
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

function validateAndSubmitForm(event) {
    event.preventDefault(); // Prevent form submission
    let allFilled = true;
    document.querySelectorAll('#mainForm input.form-control').forEach(function(input) {
        if (input.value === '') {
            allFilled = false;
        }
    });

    if (allFilled) {
        // Form is valid, proceed with submission
        const volumeGroupIdsInput = document.getElementById('volumeGroupIds');
        if (volumeGroupIdsInput) { // Check if the volumeGroupIds input exists
            volumeGroupIdsInput.value = volumeGroupIds.join(','); // Set the value
        }

        const mainForm = document.getElementById('mainForm');
        if (mainForm) { // Check if the mainForm exists before submitting
            mainForm.submit(); // This submits the form
        }
    } else {
        alert('Por favor, preencha todos os campos obrigatórios.');
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