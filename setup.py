from setuptools import setup, find_packages

setup(name='gnip_tweet_evaluation',
        packages=find_packages(),
        scripts=[
            'tweet_evaluator.py',
            ],
        version='0.1',
        license='MIT',
        author='Jeff Kolb',
        author_email='jeffakolb@gmail.com',
        description="Tools for evaluation of Tweets", 
        url='https://github.com/jeffakolb/Gnip-Tweet-Evaluation',
        install_requires=['sngrams'],
        extras_require={'plotting':['matplotlib'],'insights':['gnip_insights_interface']}
        )
