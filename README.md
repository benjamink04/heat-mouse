# Heat Mouse

Track your mouse clicking habit across web browsers, video games, and all other applications. Explore your data with an intuitive UI based in PyQt5. Automatically store Heat Mouse data in a locally accessible SQL database after every session.

## Description

Heat Mouse provides you with mouse clicking data gathering for all applications accessed by the user. The gathered data is used to actively plot your personalized clicking heat map, all while continuing to collect mouse click data using extensive threading processes. Data is fed through a Gaussian filter to provide variable levels of detail to the mouse clicking data. The intuitive UI allows users to access their heat maps for all applications that are currently in use, or have been used previously. Using a locally store SQL database, Heat Mouse will store all collected data so that it can be easily accessed at the start of your next session.

## Getting Started

### Installing

```
pip install heatmouse
```

### Executing program

```
python -m heatmouse
```

## Authors

Benjamin Katz 

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details
