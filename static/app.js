// JavaScript code for dynamic volume field management and form validation

document.addEventListener('DOMContentLoaded', function() {
    // Attach event listeners
    document.getElementById('addVolumeGroup').addEventListener('click', addVolumeGroup);
    document.addEventListener('input', updateSubmitButtonState);

    // Initialize the form with one volume group
    updateVolumeFields();
    
    // Ensure the total is correct after the initial volume group is added
    updateVolumesTotal();

    // Attach the validateAndSubmitForm function to the form's submit event
    document.getElementById('myForm').addEventListener('submit', validateAndSubmitForm);

});

let volumeGroupIds = []; // Global declaration
let volumeGroupIdCounter = 1; // Global declaration

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
                    <label for="altura${volumeGroupIdCounter}">Altura do volume:</label>
                    <input required autocomplete="off" class="form-control" type="text" name="altura${volumeGroupIdCounter}" placeholder="Altura do volume">
                </div>
                <div class="col-md-6 mb-3">
                    <label for="largura${volumeGroupIdCounter}">Largura do volume:</label>
                    <input required autocomplete="off" class="form-control" type="text" name="largura${volumeGroupIdCounter}" placeholder="Largura do volume">
                </div>
            </div>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <label for="comprimento${volumeGroupIdCounter}">Comprimento do volume:</label>
                    <input required autocomplete="off" class="form-control" type="text" name="comprimento${volumeGroupIdCounter}" placeholder="Comprimento do volume">
                </div>
                <div class="col-md-6 mb-3">
                    <label for="volumes${volumeGroupIdCounter}">Quantidade de volumes:</label>
                    <input required autocomplete="off" class="form-control" type="number" name="volumes${volumeGroupIdCounter}" placeholder="Quantidade de volumes" oninput="updateVolumesTotal()">
                </div>
                <div class="col-md-6 mb-3">
                    <button type="button" class="btn btn-danger" onclick="removeVolumeGroup(${volumeGroupIdCounter})">Remover volume</button>
                </div>
            </div>
        </div>
    `;
    volumeFieldsContainer.innerHTML += volumeGroupHTML;
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
        // Removes the volume group
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
    document.querySelectorAll('.volume-group input[type="number"]').forEach(function(input) {
        total += parseInt(input.value, 10) || 0;
    });
    document.getElementById('volumesTotal').value = total;
}

function validateAndSubmitForm(event) {
    event.preventDefault(); // Prevent form submission
    let allFilled = true;
    document.querySelectorAll('#myForm input').forEach(function(input) {
        if (input.value === '') {
            allFilled = false;
        }
    });

    if (allFilled) {
        // Form is valid, proceed with submission
        document.getElementById('volumeGroupIds').value = volumeGroupIds.join(','); // Set the value of the hidden input field as a string of volumeGroupIds

        document.getElementById('myForm').submit(); // This submits the form
    } else {
        alert('Por favor, preencha todos os campos obrigatórios.');
    }
}

function updateSubmitButtonState() {
    let allFilled = true;
    document.querySelectorAll('#myForm input').forEach(function(input) {
        if (input.value === '') {
            allFilled = false;
        }
    });

    document.getElementById('submitButton').disabled = !allFilled;
}