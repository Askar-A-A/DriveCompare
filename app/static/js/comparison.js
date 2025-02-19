document.addEventListener('DOMContentLoaded', function() {
    // Setup for Vehicle 1
    setupVehicleSelectors('1');
    // Setup for Vehicle 2
    setupVehicleSelectors('2');
});

function setupVehicleSelectors(vehicleNum) {
    const yearSelect = document.getElementById(`vehicle${vehicleNum}Year`);
    const makeSelect = document.getElementById(`vehicle${vehicleNum}Make`);
    const modelSelect = document.getElementById(`vehicle${vehicleNum}Model`);

    // Year change handler
    yearSelect.addEventListener('change', async function() {
        const year = this.value;
        
        // Reset and disable downstream selects
        makeSelect.innerHTML = '<option value="">Select Make</option>';
        modelSelect.innerHTML = '<option value="">Select Model</option>';
        makeSelect.disabled = !year;
        modelSelect.disabled = true;

        if (year) {
            try {
                const response = await fetch(`/api/makes/${year}`);
                if (!response.ok) throw new Error('Failed to fetch makes');
                const makes = await response.json();
                
                makes.forEach(make => {
                    const option = new Option(make.MakeName, make.MakeName);
                    makeSelect.add(option);
                });
                makeSelect.disabled = false;
            } catch (error) {
                console.error('Error fetching makes:', error);
                showError(`Failed to load makes for year ${year}`);
            }
        }
    });

    // Make change handler
    makeSelect.addEventListener('change', async function() {
        const make = this.value;
        const year = yearSelect.value;
        
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

function showError(message) {
    // Add error notification functionality here
    alert(message); // Basic error display for now
}
