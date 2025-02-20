document.addEventListener('DOMContentLoaded', function() {
    console.log('1. Page loaded, initializing vehicle selectors');
    setupVehicleSelectors('1');
    setupVehicleSelectors('2');
});

function setupVehicleSelectors(vehicleNum) {
    const makeSelect = document.getElementById(`vehicle${vehicleNum}Make`);
    const yearSelect = document.getElementById(`vehicle${vehicleNum}Year`);
    const modelSelect = document.getElementById(`vehicle${vehicleNum}Model`);

    makeSelect.disabled = false;
    loadMakes(makeSelect);

    makeSelect.addEventListener('change', async function() {
        const make = this.value;
        
        yearSelect.innerHTML = '<option value="">Select Year</option>';
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        yearSelect.disabled = !make;
        modelSelect.disabled = true;

        if (make) {
            try {
                const response = await fetch(`/api/years/${make}`);
                if (!response.ok) throw new Error('Failed to fetch years');
                const years = await response.json();
                
                years.forEach(year => {
                    const option = new Option(year.toString(), year);
                    yearSelect.add(option);
                });
                yearSelect.disabled = false;
            } catch (error) {
                console.error('Error fetching years:', error);
                showError(`Failed to load years for ${make}`);
            }
        }
    });

    yearSelect.addEventListener('change', async function() {
        const year = this.value;
        const make = makeSelect.value;
        
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        modelSelect.disabled = true;

        if (make && year) {
            try {
                const response = await fetch(`/api/models/${make}/${year}`);
                if (!response.ok) throw new Error('Failed to fetch models');
                const models = await response.json();
                
                models.forEach(model => {
                    const option = new Option(model.Model_Name, model.Model_Name);
                    modelSelect.add(option);
                });
                modelSelect.disabled = false;
            } catch (error) {
                console.error('Error fetching models:', error);
                showError(`Failed to load models for ${make} ${year}`);
            }
        }
    });
}

async function loadMakes(makeSelect) {
    console.log('2. Starting loadMakes function');
    try {
        console.log('3. Sending fetch request to /api/makes');
        const response = await fetch('/api/makes');
        console.log('8. Received response:', response.status);
        
        const data = await response.json();
        console.log('9. Parsed JSON data:', data);

        makeSelect.innerHTML = '<option value="">Select Make</option>';
        console.log('10. Cleared existing options');

        const makes = data.Results || data;
        console.log('11. Processed makes array:', makes);

        if (Array.isArray(makes)) {
            makes.forEach(make => {
                const makeName = make.Make_Name;
                console.log('12. Adding make:', makeName);
                const option = new Option(makeName, makeName);
                makeSelect.add(option);
            });
            console.log('13. Finished adding all makes to dropdown');
        }
    } catch (error) {
        console.error('ERROR in loadMakes:', error);
    }
}

function showError(message) {
    console.error(message);
    alert(message);
}
