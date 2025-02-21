document.addEventListener('DOMContentLoaded', function() {
    setupVehicleSelectors('1');
    setupVehicleSelectors('2');
});

function setupVehicleSelectors(vehicleNum) {
    const makeSelect = document.getElementById(`vehicle${vehicleNum}Make`);
    const yearSelect = document.getElementById(`vehicle${vehicleNum}Year`);
    const modelSelect = document.getElementById(`vehicle${vehicleNum}Model`);

    makeSelect.disabled = false;
    loadMakes(makeSelect);

    makeSelect.addEventListener('change', function() {
        const make = this.value;
        
        // Reset and disable downstream selects
        yearSelect.disabled = !make;
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        modelSelect.disabled = true;
    });

    yearSelect.addEventListener('change', async function() {
        const year = this.value;
        const make = makeSelect.value;
        
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        modelSelect.disabled = true;

        if (make && year) {
            try {
                modelSelect.innerHTML = '<option value="">Loading models...</option>';
                
                const response = await fetch(`/api/models/${make}/${year}`);
                if (!response.ok) throw new Error('Failed to fetch models');
                const models = await response.json();
                
                modelSelect.innerHTML = '<option value="">Select Model</option>';
                
                if (models.length === 0) {
                    modelSelect.innerHTML = '<option value="">No models available</option>';
                    return;
                }

                models.forEach(model => {
                    const option = new Option(model.Model_Name, model.Model_Name);
                    modelSelect.add(option);
                });
                modelSelect.disabled = false;
            } catch (error) {
                console.error('Error fetching models:', error);
                modelSelect.innerHTML = '<option value="">Error loading models</option>';
                showError(`Failed to load models for ${make} ${year}`);
            }
        }
    });
}

async function loadMakes(makeSelect) {
    try {
        const response = await fetch('/api/makes');
        
        const data = await response.json();

        makeSelect.innerHTML = '<option value="">Select Make</option>';

        const makes = data.Results || data;

        if (Array.isArray(makes)) {
            makes.forEach(make => {
                const makeName = make.Make_Name;
                const option = new Option(makeName, makeName);
                makeSelect.add(option);
            });
        }
    } catch (error) {
        console.error('ERROR in loadMakes:', error);
    }
}

function showError(message) {
    console.error(message);
    alert(message);
}
