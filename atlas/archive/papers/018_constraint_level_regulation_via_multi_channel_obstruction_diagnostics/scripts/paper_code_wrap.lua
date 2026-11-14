-- Preserve inline identifiers and hashes while allowing TeX to break long lines.
function Code(el)
  if FORMAT:match('latex') and not el.text:find('[{}\\]') then
    return pandoc.RawInline('latex', '\\nolinkurl{' .. el.text .. '}')
  end
end
