-- auto_commit_delay.lua
-- 4码无候选：由popping机制自动上屏（保持原有逻辑）
-- 4码有候选 + 继续输入第5码：立即选中第一个候选上屏，第5码开始新输入

---@param key KeyEvent
---@param env Env
local function processor(key, env)
  local context = env.engine.context
  if key:release() or key:alt() or key:ctrl() then
    return 2 -- kNoop
  end

  local input = context.input
  local input_len = #input

  -- 仅当上一轮处理后的输入为4码、且有候选菜单时触发
  if input_len == 4 and context:has_menu() then
    -- 仅字母键触发（数字键留给用户手动选候选）
    local key_repr = key:repr()
    if #key_repr == 1 and key_repr:match("[a-z]") then
      -- 自动选中第一个候选上屏
      context:confirm_current_selection()
      context:clear()
      return 2 -- kNoop，让当前按键继续被speller处理为新输入
    end
  end

  return 2
end

return { func = processor }