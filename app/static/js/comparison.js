document.addEventListener('DOMContentLoaded', function() {
    setupVehicleSelectors('1');
    setupVehicleSelectors('2');
});

function setupVehicleSelectors(vehicleNum) {
    const makeSelect = document.getElementById(`vehicle${vehicleNum}Make`);
    const typeSelect = document.getElementById(`vehicle${vehicleNum}Type`);
    const yearSelect = document.getElementById(`vehicle${vehicleNum}Year`);
    const modelSelect = document.getElementById(`vehicle${vehicleNum}Model`);

    makeSelect.disabled = false;
    loadMakes(makeSelect);

    makeSelect.addEventListener('change', function() {
        const make = this.value;
        
        // Reset and disable downstream selects
        typeSelect.innerHTML = '<option value="">Select Vehicle Type</option>';
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        
        typeSelect.disabled = !make;
        yearSelect.disabled = true;
        modelSelect.disabled = true;

        if (make) {
            loadVehicleTypes(make, typeSelect);
        }
    });

    typeSelect.addEventListener('change', function() {
        const type = this.value;
        
        // Only reset model select
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        modelSelect.disabled = true;
        
        // Enable year select if type is selected
        yearSelect.disabled = !type;
    });

    yearSelect.addEventListener('change', async function() {
        const year = this.value;
        const make = makeSelect.value;
        const vehicleType = typeSelect.value;
        
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        modelSelect.disabled = true;

        if (make && year && vehicleType) {
            loadModels(make, year, vehicleType, modelSelect);
        }
    });
}

async function loadMakes(makeSelect) {
    try {
        const response = await fetch('/api/makes');
        if (!response.ok) throw new Error('Failed to fetch makes');
        
        const data = await response.json();
        makeSelect.innerHTML = '<option value="">Select Make</option>';

        if (Array.isArray(data)) {
            data.forEach(make => {
                const makeName = make.Make_Name;
                const option = new Option(makeName, makeName);
                makeSelect.add(option);
            });
        }
    } catch (error) {
        console.error('Error loading makes:', error);
        makeSelect.innerHTML = '<option value="">Error loading makes</option>';
        showError('Failed to load vehicle makes');
    }
}

async function loadVehicleTypes(make, typeSelect) {
    try {
        typeSelect.innerHTML = '<option value="">Loading vehicle types...</option>';
        
        const response = await fetch(`/api/vehicle-types/${make}`);
        if (!response.ok) throw new Error('Failed to fetch vehicle types');
        
        const types = await response.json();
        typeSelect.innerHTML = '<option value="">Select Vehicle Type</option>';
        
        if (types.length === 0) {
            typeSelect.innerHTML = '<option value="">No vehicle types available</option>';
            return;
        }

        types.forEach(type => {
            const option = new Option(type.VehicleTypeName, type.VehicleTypeName);
            typeSelect.add(option);
        });
        typeSelect.disabled = false;
    } catch (error) {
        console.error('Error loading vehicle types:', error);
        typeSelect.innerHTML = '<option value="">Error loading vehicle types</option>';
        showError(`Failed to load vehicle types for ${make}`);
    }
}

async function loadModels(make, year, vehicleType, modelSelect) {
    try {
        modelSelect.innerHTML = '<option value="">Loading models...</option>';
        
        const response = await fetch(`/api/models/${make}/${year}/${encodeURIComponent(vehicleType)}`);
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
        console.error('Error loading models:', error);
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
        showError(`Failed to load models for ${make} ${year} ${vehicleType}`);
    }
}

function showError(message) {
    console.error(message);
    alert(message);
}
