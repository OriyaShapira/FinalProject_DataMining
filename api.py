from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # Collecting form data
    Manufactor = request.form['Manufactor']
    Model = request.form['Model']
    Year = request.form['Year']
    Hand = request.form['Hand']
    Gear = request.form['Gear']
    Capacity_Engine = request.form['Capacity_Engine']
    EngineType = request.form['Engine_Type']
    Km = request.form['Km']
    CurrentOwnership = request.form['Current']
    Area = request.form['Area']
    City = request.form['City']

    # Optional data fields
    Color = request.form.get('Color', '')
    PreviousOwnership = request.form.get('Previous', '')
    TestYear = request.form.get('Test-Year', '')
    TestMonth = request.form.get('Test-Month', '')
    Description = request.form.get('Description', '')

    # Rendering the form data into the ad format
    ad_content = f"""
        <h2>Your car details are:</h2>
        <p><strong>{Manufactor} {Model} model {Year}</strong></p>
        <p>Hand: {Hand}</p>
        <p>Gear: {Gear}</p>
        <p>Engine Capacity: {Capacity_Engine}</p>
        <p>Engine Type: {EngineType}</p>
        <p>Kilometers: {Km}</p>
        <p>Area: {Area}</p>
        <p>City: {City}</p>
        <p>Current Ownership: {CurrentOwnership}</p>
    """

    if PreviousOwnership: ad_content += f"<p>Previous Owner: {PreviousOwnership}</p>"
    if Color: ad_content += f"<p>Color: {Color}</p>"
    if TestYear and TestMonth: ad_content += f"<p>Test: {TestMonth}/{TestYear}</p>"
    if Description: ad_content += f"<p>Description: {Description}</p>"

    return render_template('index.html', prediction_text=ad_content)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
