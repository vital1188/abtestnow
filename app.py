import os
from flask import Flask, render_template, request
from statsmodels.stats.proportion import proportions_ztest
import math

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['STATIC_FOLDER'] = 'static'


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

        count = [control_conversions, variation_conversions]
        nobs = [control_visitors, variation_visitors]
        z_stat, p_value = proportions_ztest(count=count, nobs=nobs)

        relative_improvement = round(
            (variation_conversion_rate - control_conversion_rate) / control_conversion_rate * 100, 2)

        if p_value < 0.05:
            significance_level = '95% (p < 0.05)'
        else:
            significance_level = 'not significant (p >= 0.05)'

        return render_template('index.html',
                               control_conversion_rate=control_conversion_rate,
                               variation_conversion_rate=variation_conversion_rate,
                               relative_improvement=relative_improvement,
                               p_value=p_value,
                               significance_level=significance_level,
                               control_visitors_input=control_visitors,
                               control_conversions_input=control_conversions,
                               variation_visitors_input=variation_visitors,
                               variation_conversions_input=variation_conversions)

    # If request method is GET, render the template with empty input fields
    return render_template('index.html',
                           control_visitors_input='',
                           control_conversions_input='',
                           variation_visitors_input='',
                           variation_conversions_input='')


if __name__ == '__main__':
    app.run(debug=True)
