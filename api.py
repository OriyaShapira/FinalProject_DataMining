from flask import Flask, request, render_template
app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    '''
    For rendering the information entered by the user on HTML GUI
    '''
    Manufactor = request.form['Manufactor']
    Model = request.form['Model']
    Year = request.form['Year']
    Hand = request.form['Hand']
    Gear = request.form['Gear']
    Capacity_Engine = request.form['Capacity_Engine']
    EngineType = request.form['Engine_Type']
    Km = request.form['Km']
    Curr_ownership = request.form['Current']
    Area = request.form['Area']
    City = request.form['City']

    # Optional data fields
    Color = request.form.get('Color', '')
    Prev_ownership = request.form.get('Previous', '')
    Test_year = request.form.get('Test-Year', '')
    Test_month = request.form.get('Test-Month', '')
    Description = request.form.get('Description', '')

    # Rendering the form data into the ad format
    output_text = f"""
        <h2>Your car details are:</h2>
        <p><strong>{Manufactor} {Model} model {Year}</strong></p>
        <p>Hand: {Hand}</p>
        <p>Gear: {Gear}</p>
        <p>Engine Capacity: {Capacity_Engine}</p>
        <p>Engine Type: {EngineType}</p>
        <p>Kilometers: {Km}</p>
        <p>Area: {Area}</p>
        <p>City: {City}</p>
        <p>Current Ownership: {Curr_ownership}</p>
    """

    if Prev_ownership: output_text += f"<p>Previous Owner: {Prev_ownership}</p>"
    if Color: output_text += f"<p>Color: {Color}</p>"
    if (Test_year and Test_month): output_text += f"<p>Test: {Test_month}/{Test_year}</p>"
    if Description: output_text  += f"<p>Description: {Description}</p>"

    return render_template('index.html', prediction_text='{}'.format(output_text))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
