import propTypes from 'prop-types';
import React from 'react';
import ReactTable from 'react-table';
import 'react-table/react-table.css';
import '../styles/corenlp.css';

const Corenlp = (props) => {
  const { nlpData } = props;

  const tableData = nlpData;

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
  nlpData: propTypes.objectOf(propTypes.string).isRequired,
};

export default Corenlp;
