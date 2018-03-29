import propTypes from 'prop-types';
import React from 'react';
import ReactTable from 'react-table';
import 'react-table/react-table.css';
import '../styles/lexigram.css';

const Lexigram = (props) => {
  const { lexigramData } = props;

  const tableData = [];
  Object.keys(lexigramData).forEach(labelType => (
    lexigramData[labelType].map(labelValue => (
      tableData.push({
        type: labelType,
        label: labelValue.label,
        reftext: labelValue.token,
      })
    ))
  ));

  const columns = [{
    Header: 'Type',
    accessor: 'type',
  }, {
    Header: 'Label',
    accessor: 'label',
  }, {
    Header: 'Reference text',
    accessor: 'reftext',
  }];

  return (
    <div className="lexigram-data">
      <ReactTable
        data={tableData}
        columns={columns}
        showPagination={false}
        showPaginationBottom={false}
        showPageSizeOptions={false}
        minRows={0}
        showPageJump={false}
        className="lexitable"
      />
      {/* <table>
        <thead>
          <tr>
            <th>Type</th>
            <th>Label</th>
            <th>Reference text</th>
          </tr>
        </thead>
        <tbody>
          {
            Object.keys(lexigramData).forEach(labelType => (
              lexigramData[labelType].map((labelValue) => {
                console.log(labelType, labelValue.label, labelValue.token);
                return (
                  <tr>
                    <td>{labelType}</td>
                    <td>{labelValue.label}</td>
                    <td>{labelValue.token}</td>
                  </tr>
                );
              })
            ))
          }
        </tbody>
      </table> */}
    </div>
  );
};

Lexigram.propTypes = {
  lexigramData: propTypes.objectOf(propTypes.array).isRequired,
};

export default Lexigram;
