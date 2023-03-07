from scipy.stats import norm
import openai
import os
from dotenv import load_dotenv

from flask import Flask, render_template, request
from statsmodels.stats.proportion import proportions_ztest
import math

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']
model_engine = "text-davinci-003"

app = Flask(__name__)


def generate_explanation(control_conversion_rate, variation_conversion_rate, relative_improvement, significance_level):
    prompt = f"An A/B test was conducted on an ecommerce store to test the effectiveness of the Shopping Guarantee program. 50 % of users were randomly assigned to the control group and did not experience the Shopping Guarantee, while the other 50 % were assigned to the variation group and did experience the Shopping Guarantee. The results of the A/B test are as follows: Control Conversion Rate: {control_conversion_rate} % . Variation Conversion Rate: {variation_conversion_rate} % . Relative Improvement: {relative_improvement} % . Significance Level: {round( significance_level * 100, 2)}% ."
    response = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        temperature=0.5,
        max_tokens=120,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    explanation = response.choices[0].text.strip()
    return explanation


@app.route('/', methods=['GET', 'POST'])
def calculate():
    if request.method == 'POST':
        control_visitors = int(request.form['control-visitors'])
        control_conversions = int(request.form['control-conversions'])
        variation_visitors = int(request.form['variation-visitors'])
        variation_conversions = int(request.form['variation-conversions'])

        control_conversion_rate = round(
            control_conversions / control_visitors * 100, 2)
        variation_conversion_rate = round(
            variation_conversions / variation_visitors * 100, 2)

        control_std_error = math.sqrt(
            control_conversion_rate * (100 - control_conversion_rate) / control_visitors)
        variation_std_error = math.sqrt(
            variation_conversion_rate * (100 - variation_conversion_rate) / variation_visitors)

        z_score = (variation_conversion_rate - control_conversion_rate) / \
            math.sqrt(control_std_error**2 + variation_std_error**2)

        significance_level = norm.cdf(z_score)

        relative_improvement = round(
            (variation_conversion_rate - control_conversion_rate) / control_conversion_rate * 100, 2)

        openai_explanation = generate_explanation(
            control_conversion_rate, variation_conversion_rate, relative_improvement, significance_level)

        return render_template('index.html',
                               control_conversion_rate=control_conversion_rate,
                               variation_conversion_rate=variation_conversion_rate,
                               relative_improvement=relative_improvement,
                               significance_level=round(
                               significance_level * 100, 2),
                               control_visitors_input=control_visitors,
                               control_conversions_input=control_conversions,
                               variation_visitors_input=variation_visitors,
                               variation_conversions_input=variation_conversions,
                               openai_explanation=openai_explanation)

    # If request method is GET, render the template with empty input fields
    return render_template('index.html',
                           control_visitors_input='',
                           control_conversions_input='',
                           variation_visitors_input='',
                           variation_conversions_input='')



if __name__ == '__main__':
    app.run(debug=True)
