import propTypes from 'prop-types';
import React from 'react';
import ReactTable from 'react-table';
import 'react-table/react-table.css';
import '../styles/dosage.css';

const Dosage = (props) => {
  const { dosageData } = props;

  const tableData = [];
  Object.keys(dosageData).forEach(drug => (
    tableData.push({
      drug,
      dosage: dosageData[drug],
    })
  ));

  const columns = [{
    Header: 'Drug',
    accessor: 'drug',
  }, {
    Header: 'Dosage',
    accessor: 'dosage',
  }];

  return (
    <div className="dosage-data">
      <ReactTable
        data={tableData}
        columns={columns}
        showPagination={false}
        showPaginationBottom={false}
        showPageSizeOptions={false}
        minRows={0}
        showPageJump={false}
        className="dosagetable"
      />
    </div>
  );
};

Dosage.propTypes = {
  dosageData: propTypes.objectOf(propTypes.string).isRequired,
};

export default Dosage;
