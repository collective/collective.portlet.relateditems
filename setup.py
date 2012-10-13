from setuptools import setup, find_packages

version = '0.3.6'

long_description = (
    open('README.txt').read().strip()
    + '\n' +
    open('CHANGES.rst').read().strip()
)

setup(name='collective.portlet.relateditems',
      version=version,
      description="A Plone portlet to display similar items to context",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          ],
      keywords='related, categories, keywords',
      author='Rui Guerra, kiorky',
      author_email='rui AT v2 DOT nl, kiorky <kiorky@cryptelium.net>, David Jonas <david@intk.com>',
      url='https://github.com/collective/collective.portlet.relateditems',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
