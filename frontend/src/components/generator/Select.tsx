import React, { useEffect, useState } from 'react';
import Select, {
  DropdownIndicatorProps,
  GroupBase,
  OptionProps,
  components,
} from 'react-select';
import { useNavigate, useLocation } from 'react-router-dom';

import ChevronDownIcon from '../Icons/ChevronDownIcon';

// Format group labels
const formatGroupLabel = (data: GroupBase<OptionType>) => (
  <div className="flex justify-between items-center">
    <span>{data.label}</span>
  </div>
);

// Custom Single Value Component
const customSingleValue = ({ data }: { data: OptionType }) => (
  <div
    className="flex items-center -mt-5 gap-2"
    style={{
      color: 'var(--generator-color)',
    }}
  >
    {data.Icon && (
      <data.Icon
        className="w-[16px] h-[16px]"
        style={{
          fill: 'var(--generator-color)',
        }}
      />
    )}
    {data.label}
  </div>
);

// Custom Option Component
const customOption = (props: OptionProps<OptionType, false>) => {
  const { data, innerRef, innerProps, isSelected } = props;
  return (
    <div
      ref={innerRef}
      {...innerProps}
      className={`flex items-center lg:gap-2 gap-1 lg:p-2 p-1.5 lg:pl-4 pl-3 cursor-pointer rounded-md transition-all`}
      style={{
        background: isSelected
          ? 'var(--generator-color)'
          : 'rgba(243 244 246, 0.1)',
        color: isSelected ? 'white' : '',
      }}
    >
      {data.Icon && (
        <data.Icon
          className={`w-4 h-4`}
          style={{
            fill: isSelected ? 'white' : 'var(--generator-color)',
          }}
        />
      )}
      {data.label}
    </div>
  );
};

// Custom Dropdown Indicator
const customDropdownIndicator = (
  props: DropdownIndicatorProps<OptionType, false>
) => (
  <components.DropdownIndicator {...props}>
    <ChevronDownIcon
      className="w-[16px] h-[16px]"
      style={{
        stroke: 'var(--generator-color)',
      }}
    />
  </components.DropdownIndicator>
);

type Props = {
  options: GroupBase<OptionType>[];
};

const GeneratorSelect: React.FC<Props> = ({ options }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [selectedOption, setSelectedOption] = useState<OptionType | null>(null);

  // Extract "model" query parameter from URL
  useEffect(() => {
    const queryParams = new URLSearchParams(location.search);
    const model = queryParams.get('model');

    // Find the matching option
    const foundOption =
      options[0].options.find((opt) => opt.value === model) || null;

    setSelectedOption(foundOption);
    // eslint-disable-next-line
  }, [location.search]);

  return (
    <div>
      <label htmlFor="generator-select" className="sr-only">
        Selecciona un modelo
      </label>
      <Select
        id="generator-select"
        inputId="generator-select"
        options={options}
        formatGroupLabel={formatGroupLabel}
        placeholder="Select a model"
        className="lg:w-[270px] md:w-[200px] w-[170px] lg:text-sm text-xs"
        isSearchable={false}
        value={selectedOption} // Set default selected value
        onChange={(e) => {
          navigate(`/generator?model=${e?.value}`);
        }}
        styles={{
          control: (base) => ({
            ...base,
            outline: 'none',
            border: '1px solid var(--generator-color)',
            boxShadow: 'none',
            borderRadius: '16px',
            cursor: 'pointer',
            backgroundColor: 'transparent',
            color: 'white',
            ':hover': {
              border: '1px solid var(--generator-color)',
            },
          }),
          menu: (base) => ({
            ...base,
            borderRadius: '16px',
            overflow: 'hidden',
            cursor: 'pointer',
          }),
        }}
        components={{
          SingleValue: customSingleValue,
          Option: customOption,
          DropdownIndicator: customDropdownIndicator,
          IndicatorSeparator: () => null,
        }}
      />
    </div>
  );
};

export default GeneratorSelect;
