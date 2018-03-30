import propTypes from 'prop-types';
import React from 'react';
import ReactTable from 'react-table';
import 'react-table/react-table.css';
import '../styles/corenlp.css';

const Corenlp = (props) => {
  const { nlpData } = props;

  const tableData = [];
  nlpData.forEach((key, idx) => {
    if (key) {
      switch (idx) {
        case 0: tableData.push({
          type: 'Hospital',
          value: key,
        });
          break;
        case 1: tableData.push({
          type: 'Doctor',
          value: key,
        });
          break;
        case 2: tableData.push({
          type: 'Address',
          value: key,
        });
          break;
        case 3: tableData.push({
          type: 'Specialization',
          value: key,
        });
          break;
        case 4: tableData.push({
          type: 'Contact details',
          value: key,
        });
          break;
        case 5: tableData.push({
          type: 'Email address',
          value: key,
        });
          break;
        case 6: tableData.push({
          type: 'Date',
          value: key,
        });
          break;
        default: break;
      }
    }
  });

  const columns = [{
    Header: 'Entity type',
    accessor: 'type',
  }, {
    Header: 'Entity value',
    accessor: 'value',
  }];

  return (
    <div className="nlp-data">
      <ReactTable
        data={tableData}
        columns={columns}
        showPagination={false}
        showPaginationBottom={false}
        showPageSizeOptions={false}
        minRows={0}
        showPageJump={false}
        className="nlptable"
      />
    </div>
  );
};

Corenlp.propTypes = {
  nlpData: propTypes.arrayOf(propTypes.string).isRequired,
};

export default Corenlp;
