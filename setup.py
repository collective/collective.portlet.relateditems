from setuptools import setup, find_packages

version = '0.3.11.dev0'

long_description = (
    open('README.rst').read().strip()
    + '\n\n' +
    open('CHANGES.rst').read().strip()
)

setup(name='collective.portlet.relateditems',
      version=version,
      description="A Plone portlet to display similar items to context",
      long_description=long_description,
      # Get more strings from
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Framework :: Plone",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
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
